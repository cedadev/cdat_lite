/*
 * Objects representing cdunif files and variables.
 *
 * Adapted from code Written by Konrad Hinsen
 * (last revision: 2001-1-8)
 *
 * Note: Compile with -DPCMDI_NUMERICS if the PCMDI
 * Numerics module is used.
 */


#include "Python.h"
#include "Numeric/arrayobject.h"
#include "netcdf.h"

#define _CDUNIF_MODULE
#include "Cdunifmodule.h"


staticforward int Cdunif_file_init();
staticforward PyCdunifVariableObject *Cdunif_variable_new();
staticforward PyObject *PyCdunifVariableObject_subscript();
staticforward PyObject *PyCdunifVariableObject_slice();
staticforward int PyCdunifVariableObject_ass_subscript();
staticforward int PyCdunifVariableObject_ass_slice();
staticforward int nc_get_att_any(int ncid, int varid, const char *name,
			  nc_type xtype, void *data);

/* Error object and error messages for netcdf-specific errors */

static PyObject *CdunifError;

static char *netcdf_errors[] = {
  "No Error",
  "Not a netcdf id",
  "Too many netcdfs open",
  "netcdf file exists && NC_NOCLOBBER",
  "Invalid Argument",
  "Write to read only",
  "Operation not allowed in data mode",
  "Operation not allowed in define mode",
  "Coordinates out of Domain",
  "MAX_NC_DIMS exceeded",
  "String match to name in use",
  "Attribute not found",
  "MAX_NC_ATTRS exceeded",
  "Not a netcdf data type",
  "Invalid dimension id",
  "NC_UNLIMITED in the wrong index",
  "MAX_NC_VARS exceeded",
  "Variable not found",
  "Action prohibited on NC_GLOBAL varid",
  "Not a netcdf file",
  "In Fortran, string too short",
  "MAX_NC_NAME exceeded",
  "NC_UNLIMITED size already in use", /* 22 */
  "", "", "", "", "", "", "", "", "",
  "XDR error" /* 32 */
};

/* Set error string */
static void
Cdunif_seterror()
{
  if (ncerr != 0) {
    char *error = "Unknown error";
    if (ncerr > 0 && ncerr <= 32)
      error = netcdf_errors[ncerr];
    PyErr_SetString(CdunifError, error);
  }
}


/* DEBUG: dump the type of an array, recursively looking at each sub-object */
void print_array_type(char *name, PyArrayObject *array) {
  PyObject *atype;
  PyObject *zero = Py_BuildValue("i", 0);

  printf("== Dumping type of array object %s\n", name);
  do {
    atype = PyObject_Type(array);
    PyObject_Print(atype, stdout, 0);
    printf("\n");
    array = PyObject_GetItem(array, zero);
    /* New reference returned so release straight away */
    Py_DECREF(array);
  }
  while (PyArray_Check(array));

  printf("== Dump end for %s\n", name);

  Py_DECREF(zero);
}



					     /* cdunif/netCDF wrappers */

static void cdmapdatatype_cu(CuType cutype,nc_type *datatype){
	switch (cutype){
	case CuByte:
		*datatype = NC_BYTE;
		break;
	case CuChar:
		*datatype = NC_CHAR;
		break;
	case CuShort:
		*datatype = NC_SHORT;
		break;
	case CuInt:
	case CuLong:
		*datatype = NC_LONG;
		break;
	case CuFloat:
		*datatype = NC_FLOAT;
		break;
	case CuDouble:
		*datatype = NC_DOUBLE;
		break;
	default:
		*datatype = 0;
		break;
	}
	return;
}

static int cdattget(PyCdunifFileObject *file, int varid, const char* name, void* value){
    int err;
    nc_type dtype;
    int t_len;
    
    if (file->filetype==CuNetcdf) {
	err = ncattinq(file->id, varid, name, &dtype, &t_len);
	if (err==-1)
	    return -1;
	return nc_get_att_any(file->id, varid, name, dtype, value);
    }
    else
	return cuattget(file->id,varid,name,value);
}
static int cdattinq(PyCdunifFileObject *file, int varid, const char* name, nc_type* datatype, int* len){
	CuType cutype;
	int err;

	if (file->filetype==CuNetcdf)
		return ncattinq(file->id,varid,name,datatype,len);
	else{
		err = cuattinq(file->id,varid,name,&cutype,len);
		if (datatype != NULL)
			cdmapdatatype_cu(cutype,datatype);
		return err;
	}
}
static int cdattname(PyCdunifFileObject *file, int varid, int attnum, char* name){
	if (file->filetype==CuNetcdf)
		return ncattname(file->id,varid,attnum,name);
	else
		return cuattname(file->id,varid,attnum,name);
}
static int cdclose(PyCdunifFileObject *file){
	if (file->filetype==CuNetcdf)
		return ncclose(file->id);
	else
		return cuclose(file->id);
}
static int cddimget(PyCdunifFileObject *file, int dimid, void *values){
	if (file->filetype==CuNetcdf){
		char dimname[MAX_NC_NAME+1];
		float *fp;
		int cdfid;
		int dimids[MAX_VAR_DIMS];
		int dimvarid;
		long dlenbytes;
		int found;
		int ndims;
		int saveopts;
		int i;
		long length;
		long start;
		char varname[MAX_NC_NAME+1];
		nc_type nctype;
		int natts;
		
		cdfid = file->id;
		if(ncdiminq(cdfid, dimid, dimname, &length)==-1){
			return -1;
		}
		
					     /* Inquire a variable with */
					     /* - the same name as dimname, */
					     /* - a single dimension, and */
					     /* - a (single) dimension id which equals dimid */
		saveopts = ncopts;
		ncopts = 0;
		if((dimvarid = ncvarid(cdfid, dimname)) != -1){
			ncopts = saveopts;
			if(ncvarinq(cdfid, dimvarid, varname, &nctype, &ndims, dimids, &natts)==-1){
				return -1;
			}
			found = (ndims == 1 && dimids[0]==dimid);
		}
		else
			found = 0;
		ncopts = saveopts;
		
					     /* If the dimension variable was found, read it */
		if(found){
			dlenbytes = length * nctypelen(nctype);
					     /* Read the dimension */
			start = 0;
			if(values && ncvarget(cdfid, dimvarid, &start, &length, values)==-1)
				return -1;
		}
		else{
					     /* Otherwise assign the default dimension */
			if(values){
				for(i=0, fp=(float*)values; i<length; i++){
					*fp++ = (float)i;
				}
			}
		}
		return CU_SUCCESS;
		
	}
	else
		return cudimget(file->id,dimid,values);
}
static int cddimid(PyCdunifFileObject *file, const char* name){
	if (file->filetype==CuNetcdf)
		return ncdimid(file->id,name);
	else
		return cudimid(file->id,CU_GLOBAL,name);
}
/* Inquire a dimension. varname is the name of the parent variable, if the dimension is local, else has value "" */
static int cddiminq(PyCdunifFileObject *file, int dimid, char* dimname, char *dimunits, nc_type *nctype, CuDimType *dimtype, char *varname, long* length){
	int err;
	CuType cutype;
	int varid;
	char dname[MAX_NC_NAME+1];
	int cdfid;
	int dimvarid;			     /* netCDF ID of variable associated with this dimension (if any) */
	int found;			     /* True iff a dimension variable was found. */
	int ndims;
	int dimids[MAX_VAR_DIMS];
	int saveopts;
	long len;
	nc_type ncunitstype;
	int natts;
	char vname[MAX_NC_NAME+1];
	int attlen;
	
	if (file->filetype==CuNetcdf) {
		cdfid = file->id;
		if(ncdiminq(cdfid, dimid, dname, &len)==-1){
			return -1;
		}
		if(dimname) strncpy(dimname,dname,CU_MAX_NAME);
		if(length) *length = len;
		
					     /* netCDF dimensions are always global */
		if(dimtype) *dimtype = CuGlobalDim;
		if(varname) strcpy(varname,"");
		
					     /* Inquire a variable with */
					     /* - the same name as dimname, */
					     /* - a single dimension, and */
					     /* - a dimension name which equals the variable name. */
		saveopts = ncopts;
		ncopts = 0;
		if((dimvarid = ncvarid(cdfid, dname)) != -1){
			ncopts = saveopts;
			if(ncvarinq(cdfid, dimvarid, vname, nctype, &ndims, dimids, &natts)==-1){
				return -1;
			}
			found = (ndims == 1 && dimids[0]==dimid);
		}
		else
			found = 0;
		ncopts = saveopts;
		
					     /* If dimension variable was found, */
					     /* inquire the units attribute (if any) */
		if(found){
			saveopts = ncopts;
			ncopts = 0;
			if(ncattinq(cdfid, dimvarid, "units", &ncunitstype, &attlen) != -1 &&
			   ncunitstype == NC_CHAR){
				ncopts = saveopts;
				if(dimunits && cdattget(file, dimvarid, "units",dimunits)==-1)
					return -1;
			}
					     /* Dimension variable was found, but no character units string */
			else{
				if(dimunits) strcpy(dimunits,"");
			}
			ncopts = saveopts;
		}
		else{
					     /* The dimension variable was not found: */
					     /* return default units and datatype */
			if(dimunits) strcpy(dimunits,"");
			if(nctype) *nctype = NC_FLOAT;
		}
		
		return CU_SUCCESS;
	}
	else {
		err = 0;
		if(cudiminq(file->id,dimid,dimname,dimunits,&cutype,dimtype,&varid,length)==-1)
			return -1;
		if (nctype)
			cdmapdatatype_cu(cutype,nctype);
		if (varname){
			if (varid==CU_GLOBAL)
				strcpy(varname,"");
			else
				err = cuvarinq(file->id,varid,varname,NULL,NULL,NULL,NULL);
		}
		return err;
	}
}
static int cdendef(PyCdunifFileObject *file){
	if (file->filetype==CuNetcdf)
		return ncendef(file->id);
	else
		return 0;
}
static int cdgeterr(PyCdunifFileObject *file){
	if (file->filetype==CuNetcdf)
		return ncerr;
	else
		return cugeterr();
}
static int cdinquire(PyCdunifFileObject *file, int* ngdims, int* nvars, int* natts, int* recdim){
	if (file->filetype==CuNetcdf)
		return ncinquire(file->id,ngdims,nvars,natts,recdim);
	else
		return cuinquire(file->id,ngdims,nvars,natts,recdim);
}
static int cdopen(const char* controlpath, int mode, CuFileType *filetype){
					     /* Check the filetype */
	int saveopts;

	saveopts = cuErrOpts;
	cuseterropts(0);
	*filetype=CuGetFileType(controlpath);
	cuseterropts(saveopts);
	if (*filetype==CuUnknown)
		return -1;
	if (*filetype==CuNetcdf)
		return ncopen(controlpath,mode);
	else{
		if (mode==NC_WRITE){
			ncerr = 5;	     /* Write to read-only file */
			Cdunif_seterror();
			return -1;
		}
		return cuopenread(controlpath,NULL);
	}
}
static int cdredef(PyCdunifFileObject *file){
	if (file->filetype==CuNetcdf)
		return ncredef(file->id);
	else
		return 0;
}
static int cdsync(PyCdunifFileObject *file){
	if (file->filetype==CuNetcdf)
		return ncsync(file->id);
	else
		return 0;
}
static int cdvarget(PyCdunifFileObject *file, int varid, const long start[], const long count[], void* value){
	if (file->filetype==CuNetcdf)
		return ncvarget(file->id,varid,start,count,value);
	else
		return cuvarget(file->id,varid,start,count,value);
}
					     /* Use for rank 0 variables only. */
static int cdvarget1(PyCdunifFileObject *file, int varid, const long mindex[], void *value){
	long one;
	if (file->filetype==CuNetcdf)
		return ncvarget1(file->id, varid, mindex, value);
	else{
		one = 1;
		return cuvarget(file->id,varid,mindex,&one,value);
	}
}
static int cdvargets(PyCdunifFileObject *file, int varid, const long start[], const long count[], const long stride[], void *values){
	if (file->filetype==CuNetcdf)
		return ncvargetg(file->id,varid,start,count,stride,NULL,values);
	else
		return cuvargets(file->id,varid,NULL,start,count,stride,0,values);
}
static int cdvarinq(PyCdunifFileObject *file, int varid, char* name, nc_type* datatype, int* ndims, int dimids[], int* natts){
	CuType cutype;
	int err;
	
	if (file->filetype==CuNetcdf)
		return ncvarinq(file->id,varid,name,datatype,ndims,dimids,natts);
	else{
		err = cuvarinq(file->id,varid,name,&cutype,ndims,dimids,natts);
		if (datatype != NULL)
			cdmapdatatype_cu(cutype,datatype);
		return err;
	}
}

/*
 * Python equivalents to netCDF data types
 *
 * Attention: the following specification may not be fully portable.
 * The comments indicate the correct netCDF specification. The assignment
 * of Python types assumes that 'short' is 16-bit and 'int' is 32-bit.
 */

int PyCdunif_data_types[] = {-1,  /* not used */
		    PyArray_SBYTE,  /* signed 8-bit int */
		    PyArray_CHAR,   /* 8-bit character */
		    PyArray_SHORT,  /* 16-bit signed int */
		    PyArray_INT,    /* 32-bit signed int */
		    PyArray_FLOAT,  /* 32-bit IEEE float */
		    PyArray_DOUBLE  /* 64-bit IEEE float */
};

static char *dimension_types[] = {"error", "global", "local"};

/* Generic data type functions, similar to those in the Cdunif/netCDF2 interface. */

static int
nc_get_att_any(int ncid, int varid, const char *name,
	       nc_type xtype, void *data)
{
  switch (xtype) {
  case NC_BYTE:
    return nc_get_att_uchar(ncid, varid, name, (unsigned char *)data);
    break;
  case NC_CHAR:
    return nc_get_att_text(ncid, varid, name, (char *)data);
    break;
  case NC_SHORT:
    return nc_get_att_short(ncid, varid, name, (short *)data);
    break;
  case NC_INT:
    return nc_get_att_int(ncid, varid, name, (int *)data);
    break;
  case NC_FLOAT:
    return nc_get_att_float(ncid, varid, name, (float *)data);
    break;
  case NC_DOUBLE:
    return nc_get_att_double(ncid, varid, name, (double *)data);
    break;
  default:
    return NC_EINVAL;
  }
}

/* Utility functions */

static void
define_mode(file, define_flag)
     PyCdunifFileObject *file;
     int define_flag;
{
  if (file->define != define_flag) {
    if (file->define)
      cdendef(file);
    else
      cdredef(file);
    file->define = define_flag;
  }
}

static char
typecode(type)
     int type;
{
  char t;
  switch(type) {
  case PyArray_CHAR:
    t = 'c';
    break;
  case PyArray_UBYTE:
    t = 'b';
    break;
  case PyArray_SBYTE:
    t = '1';
    break;
  case PyArray_SHORT:
    t = 's';
    break;
  case PyArray_INT:
    t = 'i';
    break;
  case PyArray_LONG:
    t = 'l';
    break;
  case PyArray_FLOAT:
    t = 'f';
    break;
  case PyArray_DOUBLE:
    t = 'd';
    break;
  default: t = ' ';
  }
  return t;
}

static int
netcdf_type_from_code(code)
     char code;
{
  int type;
  switch(code) {
  case 'c':
    type = NC_CHAR;
    break;
  case 'b':
  case '1':
    type = NC_BYTE;
    break;
  case 's':
    type = NC_SHORT;
    break;
  case 'i':
  case 'l':
    type = NC_LONG;
    break;
  case 'f':
    type = NC_FLOAT;
    break;
  case 'd':
    type = NC_DOUBLE;
    break;
  default:
    type = 0;
  }
  return type;
}


static void
collect_attributes(file, varid, attributes, nattrs)
     PyCdunifFileObject *file;
     int varid;
     PyObject *attributes;
     int nattrs;
{
  char name[MAX_NC_NAME];
  nc_type type;
  int length;
  int py_type;
  int i;
  int fileid;

  fileid = file->id;
  for (i = 0; i < nattrs; i++) {
    cdattname(file, varid, i, name);
    cdattinq(file, varid, name, &type, &length);
    py_type = PyCdunif_data_types[type];
    if (py_type == PyArray_CHAR) {
      char *s = (char *)malloc((length+1)*sizeof(char));
      if (s != NULL) {
	PyObject *string;
	cdattget(file, varid, name, s);
	s[length] = '\0';
	string = PyString_FromString(s);
	if (string != NULL) {
	  PyDict_SetItemString(attributes, name, string);
	  Py_DECREF(string);
	}
	free(s);
      }
    }
    else {

      /* DEBUG */
      printf("== Calling PyArray_FromDims(1, &(%d), py_type)\n", length);

      PyObject *array = PyArray_FromDims(1, &length, py_type);

      /* DEBUG */
      print_array_type(name, array);

      if (array != NULL) {
	cdattget(file, varid, name, ((PyArrayObject *)array)->data);
	array = PyArray_Return((PyArrayObject *)array);

	if (array != NULL) {
#ifdef PCMDI_NUMERICS
	  generate_pcmdi_dims(&array,"AttributeArray");
#endif		
	  PyDict_SetItemString(attributes, name, array);
	  Py_DECREF(array);
	}
      }
    }
  }
}

static int
set_attribute(fileid, varid, attributes, name, value)
     int fileid;
     int varid;
     PyObject *attributes;
     char *name;
     PyObject *value;
{
					     /* A value of NULL means del var.attr */
					     /* was called. */
  if (value == NULL){
    if (ncattdel(fileid, varid, name) == -1){
      Cdunif_seterror();
      return -1;
    }
    PyDict_DelItemString(attributes, name);
    return 0;
  }
  else if (PyString_Check(value)) {
    if (ncattput(fileid, varid, name, NC_CHAR, PyString_Size(value),
		 PyString_AsString(value)) == -1) {
      Cdunif_seterror();
      return -1;
    }
    PyDict_SetItemString(attributes, name, value);
    return 0;
  }
  else {
    int ret;
    PyArrayObject *array =
     (PyArrayObject *)PyArray_ContiguousFromObject(value, PyArray_NOTYPE, 0, 1);
    if (array != NULL) {
      int len = (array->nd == 0) ? 1 : array->dimensions[0];
      int type = netcdf_type_from_code(array->descr->type);
      if (PyCdunif_data_types[type] != array->descr->type_num) {
	PyArrayObject *array2 = (PyArrayObject *)
	  PyArray_ContiguousFromObject((PyObject *)array,
				       PyCdunif_data_types[type], 0, 1);
	Py_DECREF(array);
	array = array2;
	if (array == NULL)
	  return -1;
      }
      ret = ncattput(fileid, varid, name, type, len, array->data);
      if (ret == -1) {
	Cdunif_seterror();
	return -1;
      }
      PyDict_SetItemString(attributes, name, (PyObject *)array);
      return 0;
    }
    else
      return -1;
  }
}

static int
check_if_open(file, mode)
     PyCdunifFileObject *file;
     int mode;
{
  /* mode: -1 read, 1 write, 0 other */
  if (file->open) {
    if (mode != 1 || file->write) {
      return 1;
    }
    else {
      PyErr_SetString(CdunifError, "write access to read-only file");
      return 0;
    }
  }
  else {
    PyErr_SetString(CdunifError, "file has been closed");
    return 0;
  }
}

/*
 * CdunifFile object
 * (type declaration in Cdunifmodule.h)
 */

/* Destroy file object */

static void
PyCdunifFileObject_dealloc(self)
     PyCdunifFileObject *self;
{
  if (self->open)
    PyCdunifFile_Close(self);
  Py_XDECREF(self->dimensions);
  Py_XDECREF(self->variables);
  Py_XDECREF(self->attributes);
  Py_XDECREF(self->name);
  Py_XDECREF(self->mode);
  Py_XDECREF(self->diminfo);
  PyObject_Del(self);			     /* PyMem_Del segfaults in 2.5 */
}

/* Create file object */

PyCdunifFileObject *
PyCdunifFile_Open(filename, mode)
     char *filename;
     char *mode;
{
  PyCdunifFileObject *self;
  int rw;
  CuFileType filetype;

  self = PyObject_NEW(PyCdunifFileObject, &PyCdunifFile_Type);
  if (self == NULL)
    return NULL;
  self->dimensions = NULL;
  self->variables = NULL;
  self->attributes = NULL;
  self->name = NULL;
  self->mode = NULL;
  self->diminfo = NULL;
  if (strlen(mode) > 2 || (strlen(mode) == 2 && mode[1] != '+')) {
    PyErr_SetString(PyExc_IOError, "illegal mode specification");
    PyCdunifFileObject_dealloc(self);
    return NULL;
  }
  rw = (strlen(mode) == 2);
  self->open = 0;
  if (mode[0] == 'w') {
    self->id = nccreate(filename, NC_CLOBBER);
    self->define = 1;
    self->write = 1;
    self->filetype = CuNetcdf;
    if (self->id != -1) {
      self->open = 1;
      Cdunif_file_init(self);
    }
  }
  else if (mode[0] == 'a') {
    self->id = cdopen(filename, NC_WRITE, &self->filetype);
    self->define = 0;
    if (self->id == -1) {
      self->id = nccreate(filename, NC_NOCLOBBER);
      self->filetype = CuNetcdf;
      self->define = 1;
    }
    self->write = 1;
    if (self->id != -1) {
      self->open = 1;
      Cdunif_file_init(self);
    }
  }
  else if (mode[0] == 'r') {
    self->id = cdopen(filename, rw ? NC_WRITE : NC_NOWRITE, &self->filetype);
    self->define = 0;
    self->write = rw;
    if (self->id != -1) {
      self->open = 1;
      Cdunif_file_init(self);
    }
  }
  else {
    PyCdunifFileObject_dealloc(self);
    return NULL;
  }
  if (self->id == -1) {
    if (self->filetype == CuUnknown){
      PyErr_SetObject(CdunifError, Py_BuildValue( "ss","Cannot open file:",filename));
    }
    else{
      Cdunif_seterror();
    }
    PyCdunifFileObject_dealloc(self);
    return NULL;
  }
  self->name = PyString_FromString(filename);
  self->mode = PyString_FromString(mode);
  return self;
}

/* Create variables from file */

static int
Cdunif_file_init(self)
     PyCdunifFileObject *self;
{
  int ndims, nvars, ngattrs, recdim;
  int i;
  char tcode;
  PyObject *tuple;
  CuDimType dimtype;
  nc_type nctype;

  self->dimensions = PyDict_New();
  self->variables = PyDict_New();
  self->attributes = PyDict_New();
  self->diminfo = PyDict_New();
  cdinquire(self, &ndims, &nvars, &ngattrs, &recdim);
  self->recdim = recdim;
  for (i = 0; i < ndims; i++) {
    char name[MAX_NC_NAME];
    char pseudoname[2*CU_MAX_NAME+1];
    char dimunits[CU_MAX_NAME+1];
    char vname[CU_MAX_NAME+1];
    long size;
    PyObject *size_ob;
    cddiminq(self, i, name, dimunits, &nctype, &dimtype, vname, &size);
    tcode = typecode(PyCdunif_data_types[nctype]);
    tuple = Py_BuildValue("(scsssi)",dimunits,tcode,name,vname,dimension_types[dimtype],i);
    if (dimtype==CuGlobalDim){
	    PyDict_SetItemString(self->diminfo, name, tuple);
	    if (i == recdim) {
		    PyDict_SetItemString(self->dimensions, name, Py_None);
	    }
	    else {
		    size_ob = PyInt_FromLong(size);
		    PyDict_SetItemString(self->dimensions, name, size_ob);
		    Py_DECREF(size_ob);
	    }
    }
    else {
	    sprintf(pseudoname,"%s_%s",name,vname);
	    PyDict_SetItemString(self->diminfo, pseudoname, tuple);
	    if (i == recdim) {
		    PyDict_SetItemString(self->dimensions, pseudoname, Py_None);
	    }
	    else {
		    size_ob = PyInt_FromLong(size);
		    PyDict_SetItemString(self->dimensions, pseudoname, size_ob);
		    Py_DECREF(size_ob);
	    }
    }
    Py_DECREF(tuple);
  }
  for (i = 0; i < nvars; i++) {
    char name[MAX_NC_NAME];
    nc_type datatype;
    int ndimensions, nattrs;
    int *dimids;
    PyCdunifVariableObject *variable;
    cdvarinq(self, i, name, &datatype, &ndimensions, NULL, &nattrs);
    if (ndimensions > 0) {
      dimids = (int *)malloc(ndimensions*sizeof(int));
      if (dimids == NULL) {
	PyErr_NoMemory();
	return 0;
      }
      cdvarinq(self, i, NULL, NULL, NULL, dimids, NULL);
    }
    else
      dimids = NULL;
    variable = Cdunif_variable_new(self, name, i, PyCdunif_data_types[datatype],
				   ndimensions, dimids, nattrs);
    if (variable != NULL) {
      PyDict_SetItemString(self->variables, name, (PyObject *)variable);
      Py_DECREF(variable);
    }
    else
      free(dimids);
  }
  collect_attributes(self, NC_GLOBAL, self->attributes, ngattrs);
  return 1;
}

/* Create dimension */

int
PyCdunifFile_CreateDimension(file, name, size)
     PyCdunifFileObject *file;
     char *name;
     long size;
{
  PyObject *size_ob;
  int id;
  if (check_if_open(file, 1)) {
    if (size == 0 && file->recdim != -1) {
      PyErr_SetString(CdunifError, "there is already an unlimited dimension");
      return -1;
    }
    define_mode(file, 1);
    id = ncdimdef(file->id, name, (size == 0) ? NC_UNLIMITED : size);
    if (id == -1) {
      Cdunif_seterror();
      return -1;
    }
    else {
      if (size == 0) {
	PyDict_SetItemString(file->dimensions, name, Py_None);
	file->recdim = id;
      }
      else {
	size_ob = PyInt_FromLong(size);
	PyDict_SetItemString(file->dimensions, name, size_ob);
	Py_DECREF(size_ob);
      }
      return 0;
    }
  }
  else
    return -1;
}

static PyObject *
PyCdunifFileObject_new_dimension(self, args)
     PyCdunifFileObject *self;
     PyObject *args;
{
  char *name;
  PyObject *size_ob;
  long size;
  if (!PyArg_ParseTuple(args, "sO", &name, &size_ob))
    return NULL;
  if (size_ob == Py_None)
    size = 0;
  else if (PyInt_Check(size_ob))
    size = PyInt_AsLong(size_ob);
  else {
    PyErr_SetString(PyExc_TypeError, "size must be None or integer");
    return NULL;
  }
  if (PyCdunifFile_CreateDimension(self, name, size) == 0) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  else
    return NULL;
}

/* Create variable */

PyCdunifVariableObject *
PyCdunifFile_CreateVariable(file, name, typecode, dimension_names, ndim)
     PyCdunifFileObject *file;
     char *name;
     int typecode;
     char **dimension_names;
     int ndim;
{
  int *dimids;
  PyCdunifVariableObject *variable;
  int ntype;
  int i;
  if (check_if_open(file, 1)) {
    define_mode(file, 1);
    if (ndim == 0)
      dimids = NULL;
    else {
      dimids = (int *)malloc(ndim*sizeof(int));
      if (dimids == NULL)
	return (PyCdunifVariableObject *)PyErr_NoMemory();
    }
    for (i = 0; i < ndim; i++) {
      dimids[i] = cddimid(file, dimension_names[i]);
      if (dimids[i] == -1) {
	Cdunif_seterror();
	free(dimids);
	return NULL;
      }
      if (dimids[i] == file->recdim && i > 0) {
	PyErr_SetString(CdunifError, "unlimited dimension must be first");
	free(dimids);
	return NULL;
      }
    }
    ntype = netcdf_type_from_code(typecode);
    i = ncvardef(file->id, name, ntype, ndim, dimids);
    if (i == -1) {
      Cdunif_seterror();
      if (dimids != NULL)
	free(dimids);
      return NULL;
    }
    variable = Cdunif_variable_new(file, name, i, PyCdunif_data_types[ntype],
				   ndim, dimids, 0);
    PyDict_SetItemString(file->variables, name, (PyObject *)variable);
    return variable;
  }
  else
    return NULL;
}

static PyObject *
PyCdunifFileObject_new_variable(self, args)
     PyCdunifFileObject *self;
     PyObject *args;
{
  PyCdunifVariableObject *var;
  char **dimension_names;
  PyObject *item, *dim;
  char *name;
  int ndim;
  char type;
  int i;
  if (!PyArg_ParseTuple(args, "scO!", &name, &type, &PyTuple_Type, &dim))
    return NULL;
  ndim = PyTuple_Size(dim);
  if (ndim == 0)
    dimension_names = NULL;
  else {
    dimension_names = (char **)malloc(ndim*sizeof(char *));
    if (dimension_names == NULL) {
      PyErr_SetString(PyExc_MemoryError, "out of memory");
      return NULL;
    }
  }
  for (i = 0; i < ndim; i++) {
    item = PyTuple_GetItem(dim, i);
    if (PyString_Check(item))
      dimension_names[i] = PyString_AsString(item);
    else {
      PyErr_SetString(PyExc_TypeError, "dimension name must be a string");
      free(dimension_names);
      return NULL;
    }
  }
  var = PyCdunifFile_CreateVariable(self, name, type, dimension_names, ndim);
  free(dimension_names);
  return (PyObject *)var;
}

/* Return a variable object referring to an existing variable */

PyCdunifVariableObject *
PyCdunifFile_GetVariable(file, name)
     PyCdunifFileObject *file;
     char *name;
{
  return (PyCdunifVariableObject *)PyDict_GetItemString(file->variables, name);
}

/* Synchronize output */

int
PyCdunifFile_Sync(file)
     PyCdunifFileObject *file;
{
  if (check_if_open(file, 0)) {
    define_mode(file, 0);
    if (cdsync(file) == -1) {
      Cdunif_seterror();
      return -1;
    }
    else
      return 0;
  }
  else
    return -1;
}

static PyObject *
PyCdunifFileObject_sync(self, args)
     PyCdunifFileObject *self;
     PyObject *args;
{
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  if (PyCdunifFile_Sync(self) == 0) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  else
    return NULL;
}

/* Close file */

int
PyCdunifFile_Close(PyCdunifFileObject *file)
{
  PyObject *name;
  PyCdunifVariableObject *variable;
  int pos, ret;

  if (!check_if_open(file, 0))
    return -1;
  ret = cdclose(file);
  if (ret != NC_NOERR) {
    Cdunif_seterror();
    ret = -1;
  }
  else
    ret = 0;
  file->open = 0;
  pos = 0;
  while (PyDict_Next(file->variables, &pos, &name, (PyObject **)&variable)) {
    Py_DECREF(variable->file);
    variable->file = NULL;
  }
  return ret;
}

static PyObject *
PyCdunifFileObject_close(self, args)
     PyCdunifFileObject *self;
     PyObject *args;
{
  char *history = NULL;
  if (!PyArg_ParseTuple(args, "|s", &history))
    return NULL;
  if (history != NULL)
    PyCdunifFile_AddHistoryLine(self, history);
  if (PyCdunifFile_Close(self) == 0) {
    Py_INCREF(Py_None);
    return Py_None;
  }
  else
    return NULL;
}

static PyObject *
PyCdunifFileObject_read_dimension(PyCdunifFileObject *self, PyObject *args){
	char *name;
	PyArrayObject *array;
	PyObject *tuple, *dimidObj;
	int dimid;
	long length;
	int dimlen;
	nc_type nctype;
	
	if (!PyArg_ParseTuple(args, "s", &name))
		return NULL;

					     /* Check that the file is open */
	if(!check_if_open(self, -1)){
		PyErr_SetString(PyExc_TypeError, "File not open");
		return NULL;
	}
					     /* Get the dimension ID */

	tuple = PyDict_GetItemString(self->diminfo,name);
	if (tuple==NULL || !PyTuple_Check(tuple)){
		PyErr_SetString(PyExc_TypeError, "Dimension not found");
		return NULL;
	}
	dimidObj = PyTuple_GetItem(tuple,5);
	if (!PyInt_Check(dimidObj)){
		PyErr_SetString(PyExc_TypeError, "Bad dimension ID");
		return NULL;
	}
	dimid = (int)PyInt_AsLong(dimidObj);

					     /* Get the dimension length and type*/
	if (cddiminq(self, dimid, NULL, NULL, &nctype, NULL, NULL, &length)==-1){
		PyErr_SetString(PyExc_TypeError, "Dimension not found in file");
		return NULL;
	}

					     /* Get the array */
	dimlen = length;
	array = (PyArrayObject *)PyArray_FromDims(1,&dimlen,PyCdunif_data_types[nctype]);
	if (array != NULL){
		if (cddimget(self, dimid, array->data)==-1){
			ncerr = cdgeterr(self);
			Cdunif_seterror();
			Py_DECREF(array);
			array=NULL;
		}
					     /* This is ugly, concatenate fails otherwise */
#ifdef PCMDI_NUMERICS
		generate_pcmdi_dims(&array,"DimensionArray");
#endif		
		return (PyObject *)array;
	}
	else {
		return PyErr_NoMemory();
	}
}

/* Method table */

static PyMethodDef PyCdunifFileObject_methods[] = {
  {"close", (PyCFunction)PyCdunifFileObject_close, 1},
  {"createDimension", (PyCFunction)PyCdunifFileObject_new_dimension, 1},
  {"createVariable", (PyCFunction)PyCdunifFileObject_new_variable, 1},
  {"readDimension",(PyCFunction)PyCdunifFileObject_read_dimension, 1},
  {"sync", (PyCFunction)PyCdunifFileObject_sync, 1},
  {NULL, NULL}		/* sentinel */
};

/* Attribute access */

PyObject *
PyCdunifFile_GetAttribute(self, name)
     PyCdunifFileObject *self;
     char *name;
{
  PyObject *value;
  if (check_if_open(self, -1)) {
    if (strcmp(name, "dimensions") == 0) {
      Py_INCREF(self->dimensions);
      return self->dimensions;
    }
    if (strcmp(name, "variables") == 0) {
      Py_INCREF(self->variables);
      return self->variables;
    }
    if (strcmp(name, "__dict__") == 0) {
      Py_INCREF(self->attributes);
      return self->attributes;
    }
    if (strcmp(name, "dimensioninfo") == 0) {
      Py_INCREF(self->diminfo);
      return self->diminfo;
    }
    value = PyDict_GetItemString(self->attributes, name);
    if (value != NULL) {
      Py_INCREF(value);
      return value;
    }
    else {
      PyErr_Clear();
      return Py_FindMethod(PyCdunifFileObject_methods, (PyObject *)self, name);
    }
  }
  else
    return NULL;
}

int
PyCdunifFile_SetAttribute(self, name, value)
     PyCdunifFileObject *self;
     char *name;
     PyObject *value;
{
  if (check_if_open(self, 1)) {
    if (strcmp(name, "dimensions") == 0 ||
	strcmp(name, "variables") == 0 ||
	strcmp(name, "dimensioninfo") == 0 ||
	strcmp(name, "__dict__") == 0) {
      PyErr_SetString(PyExc_TypeError, "object has read-only attributes");
      return -1;
    }
    define_mode(self, 1);
    return set_attribute(self->id, NC_GLOBAL, self->attributes, name, value);
  }
  else
    return -1;
}

int
PyCdunifFile_SetAttributeString(self, name, value)
     PyCdunifFileObject *self;
     char *name;
     char *value;
{
  PyObject *string = PyString_FromString(value);
  if (string != NULL)
    return PyCdunifFile_SetAttribute(self, name, string);
  else
    return -1;
}

int
PyCdunifFile_AddHistoryLine(self, text)
     PyCdunifFileObject *self;
     char *text;
{
  static char *history = "history";
  int alloc, old, new, new_alloc;
  PyStringObject *new_string;
  PyObject *h = PyCdunifFile_GetAttribute(self, history);
  if (h == NULL) {
    PyErr_Clear();
    alloc = 0;
    old = 0;
    new = strlen(text);
  }
  else {
    alloc = PyString_Size(h);
    old = strlen(PyString_AsString(h));
    new = old + strlen(text) + 1;
  }
  new_alloc = (new <= alloc) ? alloc : new + 500;
  new_string = (PyStringObject *)PyString_FromStringAndSize(NULL, new_alloc);
  if (new_string) {
    char *s = new_string->ob_sval;
    int len, ret;
    memset(s, 0, new_alloc+1);
    if (h == NULL)
      len = -1;
    else {
      strcpy(s, PyString_AsString(h));
      len = strlen(s);
      s[len] = '\n';
    }
    strcpy(s+len+1, text);
    ret = PyCdunifFile_SetAttribute(self, history, (PyObject *)new_string);
    Py_XDECREF(h);
    Py_DECREF(new_string);
    return ret;
  }
  else
    return -1;
}

/* Printed representation */
static PyObject *
PyCdunifFileObject_repr(file)
     PyCdunifFileObject *file;
{
  char buf[300];
  sprintf(buf, "<%s Cdunif file '%.256s', mode '%.10s' at %lx>",
	  file->open ? "open" : "closed",
	  PyString_AsString(file->name),
	  PyString_AsString(file->mode),
	  (long)file);
  return PyString_FromString(buf);
}

/* Type definition */

statichere PyTypeObject PyCdunifFile_Type = {
  PyObject_HEAD_INIT(NULL)
  0,		/*ob_size*/
  "CdunifFile",	/*tp_name*/
  sizeof(PyCdunifFileObject),	/*tp_basicsize*/
  0,		/*tp_itemsize*/
  /* methods */
  (destructor)PyCdunifFileObject_dealloc, /*tp_dealloc*/
  0,			/*tp_print*/
  (getattrfunc)PyCdunifFile_GetAttribute, /*tp_getattr*/
  (setattrfunc)PyCdunifFile_SetAttribute, /*tp_setattr*/
  0,			/*tp_compare*/
  (reprfunc)PyCdunifFileObject_repr,   /*tp_repr*/
  0,			/*tp_as_number*/
  0,			/*tp_as_sequence*/
  0,			/*tp_as_mapping*/
  0,			/*tp_hash*/
};

/*
 * CdunifVariable object
 * (type declaration in Cdunifmodule.h)
 */

/* Destroy variable object */

static void
PyCdunifVariableObject_dealloc(self)
     PyCdunifVariableObject *self;
{
  if (self->dimids != NULL)
    free(self->dimids);
  if (self->dimensions != NULL)
    free(self->dimensions);
  if (self->name != NULL)
    free(self->name);
  Py_XDECREF(self->file);
  Py_XDECREF(self->attributes);
  PyObject_Del(self);			     /* PyMem_Del segfaults in 2.5 */
}

/* Create variable object */

statichere PyCdunifVariableObject *
Cdunif_variable_new(file, name, id, type, ndims, dimids, nattrs)
     PyCdunifFileObject *file;
     char *name;
     int id;
     int type;
     int ndims;
     int *dimids;
     int nattrs;
{
  PyCdunifVariableObject *self;
  int recdim;
  int i;
  if (check_if_open(file, -1)) {
    self = PyObject_NEW(PyCdunifVariableObject, &PyCdunifVariable_Type);
    if (self == NULL)
      return NULL;
    self->file = file;
    Py_INCREF(file);
    self->id = id;
    self->type = type;
    self->nd = ndims;
    self->dimids = dimids;
    self->unlimited = 0;
    cdinquire(file, NULL, NULL, NULL, &recdim);
    self->dimensions = (long *)malloc(ndims*sizeof(long));
    if (self->dimensions != NULL) {
      for (i = 0; i < ndims; i++) {
	      cddiminq(file, dimids[i], NULL, NULL, NULL, NULL, NULL, &self->dimensions[i]);
      }
      if (ndims > 0 && self->dimids[0] == self->file->recdim)
	self->unlimited = 1;
    }
    self->name = (char *)malloc(strlen(name)+1);
    if (self->name != NULL)
      strcpy(self->name, name);
    self->attributes = PyDict_New();
    collect_attributes(file, self->id, self->attributes, nattrs);
    return self;
  }
  else
    return NULL;
}

/* Return value */

PyObject *
PyCdunifVariableObject_value(PyCdunifVariableObject *self, PyObject *args)
{
  PyCdunifIndex *indices;
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  if (self->nd == 0)
    indices = NULL;
  else
    indices = PyCdunifVariable_Indices(self);
  return PyArray_Return(PyCdunifVariable_ReadAsArray(self, indices));
}

/* Assign value */

PyObject *
PyCdunifVariableObject_assign(PyCdunifVariableObject *self, PyObject *args)
{
  PyObject *value;
  PyCdunifIndex *indices;
  if (!PyArg_ParseTuple(args, "O", &value))
    return NULL;
  if (self->nd == 0)
    indices = NULL;
  else
    indices = PyCdunifVariable_Indices(self);
  PyCdunifVariable_WriteArray(self, indices, value);
  Py_INCREF(Py_None);
  return Py_None;
}

/* Return typecode */

PyObject *
PyCdunifVariableObject_typecode(PyCdunifVariableObject *self, PyObject *args) {
  char t;
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  t = typecode(self->type);
  return PyString_FromStringAndSize(&t, 1);
}

/* Get an item: wrapper for subscript */
PyObject *
PyCdunifVariableObject_getitem(PyCdunifVariableObject *self, PyObject *args) {
	return PyCdunifVariableObject_subscript(self,args);
}

/* Get an item: wrapper for assign subscript */
PyObject *
PyCdunifVariableObject_setitem(PyCdunifVariableObject *self, PyObject *args) {
	PyObject *index;
	PyObject *value;
	
	if (!PyArg_ParseTuple(args, "OO", &index, &value))
		return NULL;
	if (PyCdunifVariableObject_ass_subscript(self,index,value) != -1){
		Py_INCREF(Py_None);
		return Py_None;
	}
	else
		return NULL;
}

/* Get a slice */
PyObject *
PyCdunifVariableObject_getslice(PyCdunifVariableObject *self, PyObject *args) {
  int low, high;

  if (!PyArg_ParseTuple(args, "ii", &low, &high))
	  return NULL;
  return PyCdunifVariableObject_slice(self,low,high);
}

/* Set a slice */
PyObject *
PyCdunifVariableObject_setslice(PyCdunifVariableObject *self, PyObject *args) {
  int low, high;
  PyObject *value;

  if (!PyArg_ParseTuple(args, "iiO", &low, &high, &value))
	  return NULL;
  if (PyCdunifVariableObject_ass_slice(self,low,high,value) != -1){
	  Py_INCREF(Py_None);
	  return Py_None;
  }
  else
	  return NULL;
}

/* Method table */

static PyMethodDef PyCdunifVariableObject_methods[] = {
  {"assignValue", (PyCFunction)PyCdunifVariableObject_assign, 1},
  {"getValue", (PyCFunction)PyCdunifVariableObject_value, 1},
  {"typecode", (PyCFunction)PyCdunifVariableObject_typecode, 1},
  {"getitem", (PyCFunction)PyCdunifVariableObject_getitem, 1},
  {"getslice", (PyCFunction)PyCdunifVariableObject_getslice, 1},
  {"setitem", (PyCFunction)PyCdunifVariableObject_setitem, 1},
  {"setslice", (PyCFunction)PyCdunifVariableObject_setslice, 1},
  {NULL, NULL}		/* sentinel */
};

/* Attribute access */

int
PyCdunifVariable_GetRank(var)
     PyCdunifVariableObject *var;
{
  return var->nd;
}

long *
PyCdunifVariable_GetShape(var)
     PyCdunifVariableObject *var;
{
  int i;
  if (check_if_open(var->file, -1)) {
    for (i = 0; i < var->nd; i++)
	    cddiminq(var->file, var->dimids[i], NULL, NULL, NULL, NULL, NULL, &var->dimensions[i]);
    return var->dimensions;
  }
  else
    return NULL;
}

PyObject *
PyCdunifVariable_GetAttribute(self, name)
     PyCdunifVariableObject *self;
     char *name;
{
  PyObject *value;
  if (strcmp(name, "shape") == 0) {
    PyObject *tuple;
    int i;
    if (check_if_open(self->file, -1)) {
      PyCdunifVariable_GetShape(self);
      tuple = PyTuple_New(self->nd);
      for (i = 0; i < self->nd; i++)
	PyTuple_SetItem(tuple, i, PyInt_FromLong(self->dimensions[i]));
      return tuple;
    }
    else
      return NULL;
  }
  if (strcmp(name, "dimensions") == 0) {
    PyObject *tuple;
    int i;
    if (check_if_open(self->file, -1)) {
      tuple = PyTuple_New(self->nd);
      for (i = 0; i < self->nd; i++) {
	      CuDimType dimtype;
	      char name[MAX_NC_NAME];
	      char pseudoname[2*CU_MAX_NAME+1];
	      char vname[CU_MAX_NAME+1];
	      cddiminq(self->file, self->dimids[i], name, NULL, NULL, &dimtype, vname, NULL);

	      if (dimtype==CuGlobalDim){
		      PyTuple_SetItem(tuple, i, PyString_FromString(name));
	      }
	      else {
		      sprintf(pseudoname,"%s_%s",name,vname);
		      PyTuple_SetItem(tuple, i, PyString_FromString(pseudoname));
	      }
      }
      return tuple;
    }
    else
      return NULL;
  }
  if (strcmp(name, "__dict__") == 0) {
    Py_INCREF(self->attributes);
    return self->attributes;
  }
  value = PyDict_GetItemString(self->attributes, name);
  if (value != NULL) {
    Py_INCREF(value);
    return value;
  }
  else {
    PyErr_Clear();
    return Py_FindMethod(PyCdunifVariableObject_methods, (PyObject *)self, name);
  }
}

int
PyCdunifVariable_SetAttribute(self, name, value)
     PyCdunifVariableObject *self;
     char *name;
     PyObject *value;
{
  if (check_if_open(self->file, 1)) {
    if (strcmp(name, "shape") == 0 ||
	strcmp(name, "dimensions") == 0 ||
	strcmp(name, "__dict__") == 0) {
      PyErr_SetString(PyExc_TypeError, "object has read-only attributes");
      return -1;
    }
    define_mode(self->file, 1);
    return set_attribute(self->file->id, self->id, self->attributes,
			 name, value);
  }
  else
    return -1;
}

int
PyCdunifVariable_SetAttributeString(self, name, value)
     PyCdunifVariableObject *self;
     char *name;
     char *value;
{
  PyObject *string = PyString_FromString(value);
  if (string != NULL)
    return PyCdunifVariable_SetAttribute(self, name, string);
  else
    return -1;
}

/* Subscripting */

static int
PyCdunifVariableObject_length(self)
     PyCdunifVariableObject *self;
{
  if (self->nd > 0)
    return self->dimensions[0];
  else
    return 0;
}

PyCdunifIndex *
PyCdunifVariable_Indices(var)
     PyCdunifVariableObject *var;
{
  PyCdunifIndex *indices = 
    (PyCdunifIndex *)malloc(var->nd*sizeof(PyCdunifIndex));
  int i;
  if (indices != NULL)
    for (i = 0; i < var->nd; i++) {
      indices[i].start = 0;
      indices[i].stop = var->dimensions[i];
      indices[i].stride = 1;
      indices[i].item = 0;
    }
  else
    PyErr_SetString(PyExc_MemoryError, "out of memory");
  return indices;
}

PyArrayObject *
PyCdunifVariable_ReadAsArray(self, indices)
     PyCdunifVariableObject *self;
     PyCdunifIndex *indices;
{
  int *dims;
  PyArrayObject *array;
  int i, d;
  int nitems;
  int error = 0;
  d = 0;
  nitems = 1;
  if (!check_if_open(self->file, -1)) {
    free(indices);
    return NULL;
  }
  define_mode(self->file, 0);
  if (self->nd == 0)
    dims = NULL;
  else {
    dims = (int *)malloc(self->nd*sizeof(int));
    if (dims == NULL) {
      free(indices);
      return (PyArrayObject *)PyErr_NoMemory();
    }
  }
  for (i = 0; i < self->nd; i++) {
    error = error || (indices[i].stride <= 0);
    if (indices[i].start < 0)
      indices[i].start += self->dimensions[i];
    if (indices[i].start < 0)
      indices[i].start = 0;
    if (indices[i].start > self->dimensions[i])
      indices[i].start = self->dimensions[i];
    if (indices[i].item != 0)
      indices[i].stop = indices[i].start + 1;
    else {
      if (indices[i].stop < 0)
	indices[i].stop += self->dimensions[i];
      if (indices[i].stop < 0)
	indices[i].stop = 0;
      if (indices[i].stop > self->dimensions[i])
	indices[i].stop = self->dimensions[i];
      dims[d] = (indices[i].stop-indices[i].start-1)/indices[i].stride+1;
      if (dims[d] < 0)
	dims[d] = 0;
      nitems *= dims[d];
      d++;
    }
  }
  if (error) {
    PyErr_SetString(PyExc_IndexError, "illegal index");
    if (dims != NULL)
      free(dims);
    if (indices != NULL)
      free(indices);
    return NULL;
  }
  array = (PyArrayObject *)PyArray_FromDims(d, dims, self->type);
  if (array != NULL && nitems > 0) {
    if (self->nd == 0) {
      long zero = 0;
      if (cdvarget1(self->file, self->id, &zero, array->data) == -1) {
	Cdunif_seterror();
	Py_DECREF(array);
	array = NULL;
      }
    }
    else {
      long *start;
      long *count;
      long *stride;
      start = (long *)malloc(self->nd*sizeof(long));
      count = (long *)malloc(self->nd*sizeof(long));
      stride = (long *)malloc(self->nd*sizeof(long));
      if (start != NULL && count != NULL && stride != NULL) {
	for (i = 0; i < self->nd; i++) {
	  start[i] = indices[i].start;
	  stride[i] = indices[i].stride;
	  count[i] = (indices[i].stop-indices[i].start-1)/indices[i].stride+1;
	}
	if (cdvargets(self->file, self->id, start, count, stride, array->data) == -1) {
	  Cdunif_seterror();
	  Py_DECREF(array);
	  array = NULL;
	}
#ifdef PCMDI_NUMERICS
	generate_pcmdi_dims(&array,"DataArray");
#endif
      }
      if (start != NULL)
	free(start);
      if (count != NULL)
	free(count);
      if (stride != NULL)
	free(stride);
    }
  }
  free(dims);
  free(indices);
  return array;
}

PyStringObject *
PyCdunifVariable_ReadAsString(self)
     PyCdunifVariableObject *self;
{
  if (self->type != PyArray_CHAR || self->nd != 1) {
    PyErr_SetString(CdunifError, "not a string variable");
    return NULL;
  }
  if (check_if_open(self->file, -1)) {
    long zero = 0;
    char *temp;
    PyObject *string;
    define_mode(self->file, 0);
    temp = (char *)malloc((self->dimensions[0]+1)*sizeof(char));
    if (temp == NULL)
      return (PyStringObject *)PyErr_NoMemory();
    if (cdvarget(self->file, self->id, &zero,
		 self->dimensions, temp) == -1) {
      Cdunif_seterror();
      string = NULL;
    }
    else {
      temp[self->dimensions[0]] = '\0';
      string = PyString_FromString(temp);
    }
    free(temp);
    return (PyStringObject *)string;
  }
  else
    return NULL;
}

int
PyCdunifVariable_WriteArray(self, indices, value)
     PyCdunifVariableObject *self;
     PyCdunifIndex *indices;
     PyObject *value;
{
  int *dims;
  PyArrayObject *array;
  int i, j, d;
  int nitems;
  int error = 0;
  int ret = 0;
  d = 0;
  nitems = 1;
  if (!check_if_open(self->file, 1)) {
    free(indices);
    return -1;
  }
  if (self->nd == 0)
    dims = NULL;
  else {
    dims = (int *)malloc(self->nd*sizeof(int));
    if (dims == NULL) {
      free(indices);
      PyErr_SetString(PyExc_MemoryError, "out of memory");
      return -1;
    }
  }
  define_mode(self->file, 0);
  for (i = 0; i < self->nd; i++) {
    error = error || (indices[i].stride <= 0);
    if (indices[i].start < 0)
      indices[i].start += self->dimensions[i];
    if (indices[i].start < 0)
      indices[i].start = 0;
    if (indices[i].stop < 0)
      indices[i].stop += self->dimensions[i];
    if (indices[i].stop < 0)
      indices[i].stop = 0;
    if (i > 0 || !self->unlimited) {
      if (indices[i].start > self->dimensions[i])
	indices[i].start = self->dimensions[i];
      if (indices[i].stop > self->dimensions[i])
	indices[i].stop = self->dimensions[i];
    }
    if (indices[i].item == 0) {
      dims[d] = (indices[i].stop-indices[i].start-1)/indices[i].stride+1;
      if (dims[d] < 0)
	dims[d] = 0;
      nitems *= dims[d];
      d++;
    }
    else
      indices[i].stop = indices[i].start + 1;
  }
  if (error) {
    PyErr_SetString(PyExc_IndexError, "illegal index");
    free(dims);
    free(indices);
    return -1;
  }
  array = (PyArrayObject *)PyArray_ContiguousFromObject(value, self->type,
							0, d);
  if (array != NULL) {
    if (self->nd == 0) {
      long zero = 0;
      if (ncvarput1(self->file->id, self->id, &zero, array->data) == -1) {
	Cdunif_seterror();
	ret = -1;
      }
    }
    else {
      long *start;
      long *count, *count1;
      long *stride;
      long *current;
      char *loop;
      long repeat = 1;
      int elim, lastloop;
      start = (long *)malloc(self->nd*sizeof(long));
      count = (long *)malloc(self->nd*sizeof(long));
      count1 = (long *)malloc(self->nd*sizeof(long));
      stride = (long *)malloc(self->nd*sizeof(long));
      current = (long *)malloc(self->nd*sizeof(long));
      loop = (char *)malloc(self->nd*sizeof(char));
      if (start != NULL && count != NULL && count1 != NULL
	  && stride != NULL && current != NULL && loop != NULL) {
	elim = 0;
	for (i = 0; i < self->nd; i++) {
	  start[i] = indices[i].start;
	  stride[i] = indices[i].stride;
	  count[i] = (indices[i].stop-indices[i].start-1)/indices[i].stride+1;
	  count1[i] = count[i];
	  current[i] = 0;
	  loop[i] = 0;
	  if (indices[i].item)
	    elim++;
	}
	for (i = array->nd-1, j = self->nd-1; i >= 0 && j >= 0; i--, j--) {
	  while (j >= 0 && indices[j].item)
	    j--;
	  if (j < 0) {
	    ret = -1;
	    break;
	  }
	  if (array->dimensions[i] != count[j])
	    ret = -1;
	}
	if (i == -1) {
	  lastloop = -1;
	  while (j >= 0) {
	    loop[j] = !indices[j].item;
	    if (loop[j]) {
	      if (lastloop < 0)
		lastloop = j;
	      repeat *= count[j];
	      count1[j] = 1;
	    }
	    j--;
	  }
	}
	else
	  ret = -1;
	if (ret == -1)
	  PyErr_SetString(PyExc_ValueError, "shapes are not aligned");
	while (repeat-- && ret == 0) {
	  if (ncvarputg(self->file->id, self->id, start, count1, stride, NULL,
			array->data) == -1) {
	    Cdunif_seterror();
	    ret = -1;
	  }
	  if (lastloop >= 0) {
	    for (i = lastloop; i >= 0; i--) {
	      while (!loop[i] && i >= 0)
		i--;
	      if (i >= 0) {
		start[i] += stride[i];
		if (++current[i] != count[i])
		  break;
		start[i] -= count[i]*stride[i];
		current[i] = 0;
	      }
	    }
	  }
	}
	if (self->unlimited)
	  cddiminq(self->file, self->dimids[0], NULL, NULL, NULL, NULL, NULL, &self->dimensions[0]);
      }
      Py_DECREF(array);
      if (start != NULL)
	free(start);
      if (count != NULL)
	free(count);
      if (count1 != NULL)
	free(count1);
      if (stride != NULL)
	free(stride);
      if (current != NULL)
	free(current);
      if (loop != NULL)
	free(loop);
    }
    free(dims);
    free(indices);
    return ret;
  }
  else
    return -1;
}

int
PyCdunifVariable_WriteString(self, value)
     PyCdunifVariableObject *self;
     PyStringObject *value;
{
  long zero = 0;
  long len;
  if (self->type != PyArray_CHAR || self->nd != 1) {
    PyErr_SetString(CdunifError, "not a string variable");
    return -1;
  }
  len = PyString_Size((PyObject *)value);
  if (len > self->dimensions[0]) {
    PyErr_SetString(PyExc_ValueError, "string too long");
    return -1;
  }
  if (self->dimensions[0] > len)
    len++;
  if (check_if_open(self->file, 1)) {
    define_mode(self->file, 0);
    if (ncvarput(self->file->id, self->id, &zero, &len,
		 PyString_AsString((PyObject *)value)) == -1) {
      Cdunif_seterror();
      return -1;
    }
    return 0;
  }
  else
    return -1;
}

static PyObject *
PyCdunifVariableObject_item(self, i)
     PyCdunifVariableObject *self;
     int i;
{
  PyCdunifIndex *indices;
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return NULL;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    indices[0].start = i;
    indices[0].stop = i+1;
    indices[0].item = 1;
    return PyArray_Return(PyCdunifVariable_ReadAsArray(self, indices));
  }
  return NULL;
}

static PyObject *
PyCdunifVariableObject_slice(self, low, high)
     PyCdunifVariableObject *self;
     int low;
     int high;
{
  PyCdunifIndex *indices;
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return NULL;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    indices[0].start = low;
    indices[0].stop = high;
    return PyArray_Return(PyCdunifVariable_ReadAsArray(self, indices));
  }
  return NULL;
}

static PyObject *
PyCdunifVariableObject_subscript(self, index)
     PyCdunifVariableObject *self;
     PyObject *index;
{
  PyCdunifIndex *indices;
  if (PyInt_Check(index)) {
    int i = PyInt_AsLong(index);
    return PyCdunifVariableObject_item(self, i);
  }
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return NULL;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    if (PySlice_Check(index)) {
      PySlice_GetIndices((PySliceObject *)index, self->dimensions[0],
			 &indices->start, &indices->stop, &indices->stride);
      return PyArray_Return(PyCdunifVariable_ReadAsArray(self, indices));
    }
    if (PyTuple_Check(index)) {
      int ni = PyTuple_Size(index);
      if (ni <= self->nd) {
	int i, d;
	d = 0;
	for (i = 0; i < ni; i++) {
	  PyObject *subscript = PyTuple_GetItem(index, i);
	  if (PyInt_Check(subscript)) {
	    int n = PyInt_AsLong(subscript);
	    indices[d].start = n;
	    indices[d].stop = n+1;
	    indices[d].item = 1;
	    d++;
	  }
	  else if (PySlice_Check(subscript)) {
	    PySlice_GetIndices((PySliceObject *)subscript, self->dimensions[d],
			       &indices[d].start, &indices[d].stop,
			       &indices[d].stride);
	    d++;
	  }
	  else if (subscript == Py_Ellipsis) {
	    d = self->nd - ni + i + 1;
	  }
	  else {
	    PyErr_SetString(PyExc_TypeError, "illegal subscript type");
	    free(indices);
	    return NULL;
	  }
	}
	return PyArray_Return(PyCdunifVariable_ReadAsArray(self, indices));
      }
      else {
	PyErr_SetString(PyExc_IndexError, "too many subscripts");
	free(indices);
	return NULL;
      }
    }
    PyErr_SetString(PyExc_TypeError, "illegal subscript type");
    free(indices);
  }
  return NULL;
}

static int
PyCdunifVariableObject_ass_item(self, i, value)
     PyCdunifVariableObject *self;
     int i;
     PyObject *value;
{
  PyCdunifIndex *indices;
  if (value == NULL) {
    PyErr_SetString(PyExc_ValueError, "Can't delete elements.");
    return -1;
  }
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return -1;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    indices[0].start = i;
    indices[0].stop = i+1;
    indices[0].item = 1;
    return PyCdunifVariable_WriteArray(self, indices, value);
  }
  return -1;
}

static int
PyCdunifVariableObject_ass_slice(self, low, high, value)
     PyCdunifVariableObject *self;
     int low;
     int high;
     PyObject *value;
{
  PyCdunifIndex *indices;
  if (value == NULL) {
    PyErr_SetString(PyExc_ValueError, "Can't delete elements.");
    return -1;
  }
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return -1;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    indices[0].start = low;
    indices[0].stop = high;
    return PyCdunifVariable_WriteArray(self, indices, value);
  }
  return -1;
}

static int
PyCdunifVariableObject_ass_subscript(self, index, value)
     PyCdunifVariableObject *self;
     PyObject *index;
     PyObject *value;
{
  PyCdunifIndex *indices;
  if (PyInt_Check(index)) {
    int i = PyInt_AsLong(index);
    return PyCdunifVariableObject_ass_item(self, i, value);
  }
  if (value == NULL) {
    PyErr_SetString(PyExc_ValueError, "Can't delete elements.");
    return -1;
  }
  if (self->nd == 0) {
    PyErr_SetString(PyExc_TypeError, "Not a sequence");
    return -1;
  }
  indices = PyCdunifVariable_Indices(self);
  if (indices != NULL) {
    if (PySlice_Check(index)) {
      PySlice_GetIndices((PySliceObject *)index, self->dimensions[0],
			 &indices->start, &indices->stop, &indices->stride);
      return PyCdunifVariable_WriteArray(self, indices, value);
    }
    if (PyTuple_Check(index)) {
      int ni = PyTuple_Size(index);
      if (ni <= self->nd) {
	int i, d;
	d = 0;
	for (i = 0; i < ni; i++) {
	  PyObject *subscript = PyTuple_GetItem(index, i);
	  if (PyInt_Check(subscript)) {
	    int n = PyInt_AsLong(subscript);
	    indices[d].start = n;
	    indices[d].stop = n+1;
	    indices[d].item = 1;
	    d++;
	  }
	  else if (PySlice_Check(subscript)) {
	    PySlice_GetIndices((PySliceObject *)subscript, self->dimensions[d],
			       &indices[d].start, &indices[d].stop,
			       &indices[d].stride);
	    d++;
	  }
	  else if (subscript == Py_Ellipsis) {
	    d = self->nd - ni + i + 1;
	  }
	  else {
	    PyErr_SetString(PyExc_TypeError, "illegal subscript type");
	    free(indices);
	    return -1;
	  }
	}
	return PyCdunifVariable_WriteArray(self, indices, value);
      }
      else {
	PyErr_SetString(PyExc_IndexError, "too many subscripts");
	free(indices);
	return -1;
      }
    }
    PyErr_SetString(PyExc_TypeError, "illegal subscript type");
    free(indices);
  }
  return -1;
}

/* Type definition */

static PyObject *
PyCdunifVariableObject_error1(self, other)
     PyCdunifVariableObject *self;
     PyCdunifVariableObject *other;
{
  PyErr_SetString(PyExc_TypeError, "can't add Cdunif variables");
  return NULL;
}

static PyObject *
PyCdunifVariableObject_error2(self, n)
     PyCdunifVariableObject *self;
     int n;
{
  PyErr_SetString(PyExc_TypeError, "can't multiply Cdunif variables");
  return NULL;
}


static PySequenceMethods PyCdunifVariableObject_as_sequence = {
  (inquiry)PyCdunifVariableObject_length,		/*sq_length*/
  (binaryfunc)PyCdunifVariableObject_error1,       /*nb_add*/
  (intargfunc)PyCdunifVariableObject_error2,       /*nb_multiply*/
  (intargfunc)PyCdunifVariableObject_item,		/*sq_item*/
  (intintargfunc)PyCdunifVariableObject_slice,	/*sq_slice*/
  (intobjargproc)PyCdunifVariableObject_ass_item,	/*sq_ass_item*/
  (intintobjargproc)PyCdunifVariableObject_ass_slice,   /*sq_ass_slice*/
};

static PyMappingMethods PyCdunifVariableObject_as_mapping = {
  (inquiry)PyCdunifVariableObject_length,		/*mp_length*/
  (binaryfunc)PyCdunifVariableObject_subscript,	      /*mp_subscript*/
  (objobjargproc)PyCdunifVariableObject_ass_subscript,   /*mp_ass_subscript*/
};

statichere PyTypeObject PyCdunifVariable_Type = {
  PyObject_HEAD_INIT(NULL)
  0,		     /*ob_size*/
  "CdunifVariable",  /*tp_name*/
  sizeof(PyCdunifVariableObject),	     /*tp_basicsize*/
  0,		     /*tp_itemsize*/
  /* methods */
  (destructor)PyCdunifVariableObject_dealloc, /*tp_dealloc*/
  0,			/*tp_print*/
  (getattrfunc)PyCdunifVariable_GetAttribute, /*tp_getattr*/
  (setattrfunc)PyCdunifVariable_SetAttribute, /*tp_setattr*/
  0,			/*tp_compare*/
  0,			/*tp_repr*/
  0,			/*tp_as_number*/
  &PyCdunifVariableObject_as_sequence,	/*tp_as_sequence*/
  &PyCdunifVariableObject_as_mapping,	/*tp_as_mapping*/
  0,			/*tp_hash*/
};


/* Creator for CdunifFile objects */

static PyObject *
CdunifFile(self, args)
     PyObject *self; /* Not used */
     PyObject *args;
{
  char *filename;
  char *mode = NULL;
  char *history = NULL;
  PyCdunifFileObject *file;

  if (!PyArg_ParseTuple(args, "s|ss:CdunifFile", &filename, &mode, &history))
    return NULL;
  if (mode == NULL)
    mode = "r";
  file = PyCdunifFile_Open(filename, mode);
  if (file == NULL) {
    Cdunif_seterror();
    return NULL;
  }
  if (history != NULL)
    PyCdunifFile_AddHistoryLine(file, history);
  return (PyObject *)file;
}

/* Table of functions defined in the module */

static PyMethodDef Cdunif_methods[] = {
  {"CdunifFile",	CdunifFile, 1},
  {NULL,		NULL}		/* sentinel */
};

/* Module initialization */

void
initCdunif()
{
  PyObject *m, *d;
  static void *PyCdunif_API[PyCdunif_API_pointers];

  /* Initialize netcdf and cdunif variables */
  ncopts = 0;
  cuseterropts(CU_VERBOSE);

  /* Initialize type object headers */
  PyCdunifFile_Type.ob_type = &PyType_Type;
  PyCdunifVariable_Type.ob_type = &PyType_Type;

  /* Create the module and add the functions */
  m = Py_InitModule("Cdunif", Cdunif_methods);

  /* Import the array module */
#ifdef import_array
  import_array();
#endif

  /* Add error object the module */
  d = PyModule_GetDict(m);
  CdunifError = PyString_FromString("CdunifError");
  PyDict_SetItemString(d, "CdunifError", CdunifError);

  /* Initialize C API pointer array and store in module */
  PyCdunif_API[PyCdunifFile_Type_NUM] = (void *)&PyCdunifFile_Type;
  PyCdunif_API[PyCdunifVariable_Type_NUM] = (void *)&PyCdunifVariable_Type;
  PyCdunif_API[PyCdunifFile_Open_NUM] = (void *)&PyCdunifFile_Open;
  PyCdunif_API[PyCdunifFile_Close_NUM] = (void *)&PyCdunifFile_Close;
  PyCdunif_API[PyCdunifFile_Sync_NUM] = (void *)&PyCdunifFile_Sync;
  PyCdunif_API[PyCdunifFile_CreateDimension_NUM] =
    (void *)&PyCdunifFile_CreateDimension;
  PyCdunif_API[PyCdunifFile_CreateVariable_NUM] =
    (void *)&PyCdunifFile_CreateVariable;
  PyCdunif_API[PyCdunifFile_GetVariable_NUM] =
    (void *)&PyCdunifFile_GetVariable;
  PyCdunif_API[PyCdunifVariable_GetRank_NUM] =
    (void *)&PyCdunifVariable_GetRank;
  PyCdunif_API[PyCdunifVariable_GetShape_NUM] =
    (void *)&PyCdunifVariable_GetShape;
  PyCdunif_API[PyCdunifVariable_Indices_NUM] =
    (void *)&PyCdunifVariable_Indices;
  PyCdunif_API[PyCdunifVariable_ReadAsArray_NUM] =
    (void *)&PyCdunifVariable_ReadAsArray;
  PyCdunif_API[PyCdunifVariable_ReadAsString_NUM] =
    (void *)&PyCdunifVariable_ReadAsString;
  PyCdunif_API[PyCdunifVariable_WriteArray_NUM] =
    (void *)&PyCdunifVariable_WriteArray;
  PyCdunif_API[PyCdunifVariable_WriteString_NUM] =
    (void *)&PyCdunifVariable_WriteString;
  PyCdunif_API[PyCdunifFile_GetAttribute_NUM] =
    (void *)&PyCdunifFile_GetAttribute;
  PyCdunif_API[PyCdunifFile_SetAttribute_NUM] =
    (void *)&PyCdunifFile_SetAttribute;
  PyCdunif_API[PyCdunifFile_SetAttributeString_NUM] =
    (void *)&PyCdunifFile_SetAttributeString;
  PyCdunif_API[PyCdunifVariable_GetAttribute_NUM] =
    (void *)&PyCdunifVariable_GetAttribute;
  PyCdunif_API[PyCdunifVariable_SetAttribute_NUM] =
    (void *)&PyCdunifVariable_SetAttribute;
  PyCdunif_API[PyCdunifVariable_SetAttributeString_NUM] =
    (void *)&PyCdunifVariable_SetAttributeString;
  PyCdunif_API[PyCdunifFile_AddHistoryLine_NUM] =
    (void *)&PyCdunifFile_AddHistoryLine;
  PyDict_SetItemString(d, "_C_API",
		       PyCObject_FromVoidPtr((void *)PyCdunif_API, NULL));

  /* Check for errors */
  if (PyErr_Occurred())
    Py_FatalError("can't initialize module Cdunif");
}
