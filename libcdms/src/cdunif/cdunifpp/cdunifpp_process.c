/*
 *
 *    Copyright (C) 2004-2006 NERC DataGrid
 *    This software may be distributed under the terms of the
 *    CCLRC Licence for CCLRC Software
 * <CDATDIR>/External_License/CCLRC_CDAT_License.txt 
 *
 */
#ifdef HAVE_PP
#include "cdunifpp.h"

/*
 *  pp_process is the routine which does the bulk of the work
 *
 *  It is called from cuopenread_pp after calling pp_read_all_headers, and it
 *  works out all the variables, dimensions and attributes.
 *
 */

int pp_process(CuFile *file)
{
  int rec, nrec, at_start_rec, at_end_rec;
  PPfile *ppfile;
  PPfieldvar *fvar;
  PPrec *recp;
  PPhdr *hdrp;
  PPgenaxis *xaxis, *yaxis, *zaxis, *taxis; /* JAK 2005-01-05 */
  PPlevel *lev;
  PPtime *time;
  PPlist *heaplist;
  PPlist *fieldvars;
  PPlisthandle handle, thandle;
  PPlist *gatts,*catts;

  int vrec, nvrec, nz, nt, z_t_reg ; /* needed for check on variables */
  PPrec *vrecp;

  int ndims, dimid;
  int idim; /* dim number of given type */
  int have_time_mean, tmdimid; /* dimensions used for meaning (CF cell methods) */
  CuDim *cudims,*dim;
  PPdim *ppdim;
  int n1dimid; /* size-1 dimension used for scalars (why not true scalar?) */

  int nvars, varid, cvarid;
  int ncvars; /* coord vars */
  int nfvars; /* field vars */
  CuVar *cuvars,*var;  
  PPvar *ppvar;
  PPlist *axislist;
  PPlist *xaxes, *yaxes, *taxes, *zaxes; /* JAK 2005-01-05 */
  PPgenaxis *axis;  /*JAK 2005-01-10 */
  int have_hybrid_sigmap;
  PPaxistype axistype;

  int rotmapid, rotgridid;
  PPlist *rotgrids, *rotmaps;
  PProtmap *rotmap;
  PProtgrid *rotgrid;
  CuVar *lonvar, *latvar;  
  PPvar *lonppvar, *latppvar;

  PPlandmask *landmask;

  char *varnamea, *varnameb;

  char dimnamestem[CU_MAX_NAME], units[CU_MAX_NAME];
  PPstashmeta stashmeta;
  char formulaterms[MAX_ATT_LEN+1],cellmethods[MAX_ATT_LEN+1];
  char input_uri[MAX_ATT_LEN+1],current_directory[MAX_ATT_LEN+1];

  int skip_this_variable, dont_free_horiz_axes;
  char *skip_reason;

  void *fill_ptr;

  /* temporary variables when setting attributes 
   * (must be Fint, Freal because pointers are generated)
   */
  Fint intattval;
  /* Freal realattval; */

  int bigend;

  int added;
  int ilen1, ilen2;

  int has_cellmethod;
  char tmpstring[MAX_ATT_LEN+1];

  int zindex,tindex,dindex,svindex,prev_zindex,prev_tindex,prev_dindex;

  /* ------------------------------------------------------ */  
  /* initialisation constants which matter */
  ncvars = 0;
  have_hybrid_sigmap = 0;
  have_time_mean = 0;
  svindex = 0;

  /* initialisation constants just to avoid compiler warnings
   * (rather than get accustomed to ignoring warnings)
   * but flow logic should mean that these vars do actually get
   * initialised elsewhere before use
   */
  at_end_rec=0;
  xaxis=yaxis=NULL;
  fvar=NULL;
  zaxis=NULL;
  taxis=NULL;
  axislist=NULL;
  tmdimid=-1;
  skip_this_variable=dont_free_horiz_axes=0;
  skip_reason=NULL;
  prev_zindex=prev_tindex=prev_dindex=0;
  /* ------------------------------------------------------ */

  ppfile = file->internp;

  heaplist=ppfile->heaplist;

  nrec = ppfile->nrec;  

  /* initialise disambig_index prior to initial sorting */
  for (rec=0; rec<nrec ; rec++) {
    recp = ppfile->recs[rec];
    recp->disambig_index=-1;
    recp->supervar_index=-1;
  }

  /* sort the records */
  qsort(ppfile->recs, nrec, sizeof(PPrec*), pp_compare_records);  

  /* tmp space for global attributes */
  CKP(   gatts = pp_list_new(heaplist)   );

  /* now sort out the list of variables and dimensions */

  CKP(   fieldvars=pp_list_new(heaplist)   );
  CKP(   xaxes=pp_list_new(heaplist)   );
  CKP(   yaxes=pp_list_new(heaplist)   );
  CKP(   zaxes=pp_list_new(heaplist)   );
  CKP(   taxes=pp_list_new(heaplist)   );
  CKP(   rotmaps=pp_list_new(heaplist)  );
  CKP(   rotgrids=pp_list_new(heaplist)  );

  /* before main loop over records, look for land mask */
  for (rec=0; rec<nrec ; rec++) {

    recp = ppfile->recs[rec];
    hdrp = &recp->hdr;    

    if (pp_var_is_land_mask(hdrp)) {
      
      CKP(   landmask = pp_malloc(sizeof(PPlandmask),heaplist)   );

      CKI(  pp_set_horizontal_axes(recp,ppfile,&xaxis,&yaxis,rotmaps,heaplist)  );

      CKP(   landmask->data = pp_data_new(inttype,pp_genaxis_len(xaxis) * pp_genaxis_len(yaxis),heaplist)   ); /* JAK 2005-01-05 */

      /* read in land mask data values */

      landmask->xaxis = xaxis;
      landmask->yaxis = yaxis;
      CKP(   landmask->data->values=pp_read_data_record(recp,ppfile,heaplist)   );

      ppfile->landmask = landmask;

    }	
  }

  /* ====== START LOOP OVER RECORDS ====== */

  for (rec=0; rec<nrec ; rec++) {

    recp = ppfile->recs[rec];
    hdrp = &recp->hdr;

    /* we are at start record of a variable at the very start, or if at we were at the
     * end record last time
     */
    at_start_rec = ( rec == 0 || at_end_rec );

    /* we are at end record of a variable at the very end, or if the header shows a 
     * difference from the next record which constitutes a different variable
     */
    at_end_rec = ( rec == nrec-1 ||
		   pp_records_from_different_vars(ppfile->recs[rec+1],recp));
    
    /*------------------------------*/
    /* allow for variables which are unsupported for some reason */

    if (at_start_rec) {

      skip_this_variable = 0;
      
      skip_reason=NULL;

      if (pp_var_is_missing(hdrp))
	skip_reason="PP record has essential header data set to missing data value";

      /* Compressed field index */
      if (pp_get_var_compression(hdrp) == 1)
	skip_reason="compressed field index not supported";

      if (pp_get_var_compression(hdrp) == 2 && ppfile->landmask==NULL)
	skip_reason="land/sea mask compression used but landmask field absent";

      /* ADD ANY MORE VARIABLE SKIPPING CASES HERE. */

      if (pp_grid_supported(hdrp) == 0)
	skip_reason="grid code not supported";

      if (skip_reason!=NULL) {
      	skip_this_variable = 1; 
	CuError(CU_EOPEN,"skipping variable stash code=%d,%d,%d because: %s",
		pp_get_var_stash_model(hdrp),
		pp_get_var_stash_section(hdrp),
		pp_get_var_stash_item(hdrp),
		skip_reason);
      }
    };
    
    if (skip_this_variable)
      continue;
    
    /*------------------------------*/
    /* printf("processing record %d / %d\n",rec,nrec); */
    /* pp_dump_header(hdrp); */



    if (at_start_rec) {
      /* ====== THINGS DONE ONLY AT START RECORD OF EACH VARIABLE ====== */

      /* get PPvar structure, and initialise certain structure members for tidiness */
      CKP(   fvar=pp_malloc(sizeof(PPfieldvar), heaplist)   );
      CKP(   fvar->axes=pp_list_new(heaplist)  );  /* JAK 2005-01-05 */
      fvar->startrec = rec;

      if (pp_get_var_compression(hdrp) == 2) {
	/* land/sea mask compression: for horiz axes use those of LSM */
	xaxis = ppfile->landmask->xaxis;
	yaxis = ppfile->landmask->yaxis;
	dont_free_horiz_axes = 1;
      } else {

	CKI(  pp_set_horizontal_axes(recp,ppfile,&xaxis,&yaxis,rotmaps,heaplist)  );

	dont_free_horiz_axes = 0;
      }

      CKP(   zaxis=pp_genaxis_new(zaxis_type,zdir,heaplist)   );
      CKI(  pp_zaxis_set(zaxis,hdrp)  );

      CKP(   taxis=pp_genaxis_new(taxis_type,tdir,heaplist)   );
      CKI(  pp_taxis_set(taxis,hdrp)  );

    }

    /* construct pp_lev struct, and add it to the z axis if not already present
     * (could already be present if field has multiple times on each level)
     */

    /* ====== THINGS DONE FOR EVERY PP RECORD ====== */

    /* store level info */
    CKP(  lev=pp_malloc(sizeof(PPlevel), heaplist)  );
    CKI(  pp_lev_set(lev,hdrp)  );
    CKI(  pp_zaxis_add(zaxis,lev,&zindex,heaplist)  );
    recp->zindex=zindex;

    /* store time info */
    CKP(  time=pp_malloc(sizeof(PPtime), heaplist)  );
    CKI(  pp_time_set(time, hdrp)  );
    CKI(  pp_taxis_add(taxis,time,&tindex,heaplist)  );
    recp->tindex=tindex;
    

    /* ===================================================== */
    if (at_end_rec) {
     /* ====== THINGS DONE ONLY AT END RECORD OF EACH VARIABLE ====== */

      fvar->endrec=rec;

      nvrec=fvar->endrec-fvar->startrec+1;
      nz=pp_genaxis_len(zaxis);
      nt=pp_genaxis_len(taxis);

      /*------------------------------------------------------------*/

      /* now test t and z indices to check whether the variable is on regular array of times and levels 
       * (NB "regular" here refers to the ordering, not to whether the spacing is uniform)
       */
      z_t_reg=1;
      
      /* first test the most obvious case of irregular (for possible speed) */
      if (nvrec != nz * nt)
      	z_t_reg = 0;

      /* z indices (faster varying) should loop be vrec % nz */
      /* t indices (slower varying) should loop be vrec / nz */
      if (z_t_reg) {
	for (vrec=0; vrec<nvrec; vrec++) {
	  vrecp = ppfile->recs[fvar->startrec+vrec];
	  if (vrecp->zindex != vrec%nz || vrecp->tindex != vrec/nz) {
	    z_t_reg=0;
	    break;
	  }
	}
      }
      
      /* now if the axes are not regular, free the axes, split the variable into a number of variables and try again... */

      if (!z_t_reg) {	

	/* increment the supervar index, used later to show the connection between
	 *  the separate variables into which this one will be split
	 */
	svindex++;

	/* Set the disambiguate index on each record such as to split into number of variables.
	 * The algorithm for this is quite simplistic (a separate variable for each level, further separate
	 * variables for any repeated level-and-time combinations), but could later be replaced with a more
	 * "intelligent" algorithm which minimises the number of variables subject to the regular axes
	 * constraints.
	 */
	for (vrec=0; vrec<nvrec; vrec++) {
	  vrecp = ppfile->recs[fvar->startrec+vrec];
	  
	  zindex = vrecp->zindex;
	  tindex = vrecp->tindex;

	  /* check for dups coord pairs */
	  /* the exact expressions for dindex are fairly arbitrary -- just need to ensure that
	   * indices for dup coordinate pairs will be different from indices for non-dups on other levels
	   */
	  if (vrec > 0 
	      && zindex == prev_zindex
	      && tindex == prev_tindex) {

	    dindex = prev_dindex + 1;

	  } else {

	    dindex = zindex * nvrec;
	  }
	  
	  /*
	   * printf("rec %d, height %f, day %d hour %d, disambig index set to %d\n",vrec,vrecp->hdr.BLEV,vrecp->hdr.LBDAT,vrecp->hdr.LBHR,
	   *        dindex);
	   */

	  vrecp->disambig_index = dindex;

	  if (vrecp->supervar_index < 0)
	    vrecp->supervar_index = svindex;

	  /* save vals for next iter */
	  prev_zindex=zindex;
	  prev_tindex=tindex;
	  prev_dindex=dindex;
	}

	/* now re-sort this part of the record list, now that we have set the disambig index */
	qsort(ppfile->recs + fvar->startrec, nvrec, sizeof(PPrec*), pp_compare_records);  

	/* free the stuff assoc with the var we won't be using */
	CKI(  pp_genaxis_free(xaxis,heaplist)  );
	CKI(  pp_genaxis_free(yaxis,heaplist)  );
	CKI(  pp_genaxis_free(zaxis,heaplist)  );
	CKI(  pp_genaxis_free(taxis,heaplist)  );
	CKI(  pp_free(fvar,heaplist)  );

	/* now go back to the start record of the variable; set to one less because it
	 * will get incremented in the "for" loop reinitialisation
	 */
	rec = fvar->startrec - 1;
	continue;
      }
      /*------------------------------------------------------------*/

      /*
       * For each axis, see if it matches an axis which already exists from a previous
       * variable.
       *
       * If so, then free the structure and point to the existing occurrence instead.
       *
       * If not, then add to the list.
       */

      /* x */
      CKI(  added = pp_list_add_or_find(xaxes, &xaxis, pp_genaxis_compare, 0, 
					(dont_free_horiz_axes ? NULL : (free_func) pp_genaxis_free),
					NULL, heaplist)  );
      if (added)
	ncvars++;

      /* y */
      CKI(  added = pp_list_add_or_find(yaxes, &yaxis, pp_genaxis_compare, 0, 
					(dont_free_horiz_axes ? NULL : (free_func) pp_genaxis_free),
					NULL, heaplist)  );
      if (added)
	ncvars++;

      /* z */
      CKI(  added = pp_list_add_or_find(zaxes, &zaxis, pp_genaxis_compare, 0, 
					(free_func) pp_genaxis_free,
					NULL, heaplist)  );
      if (added) {
	ncvars++;
	if (pp_zaxis_lev_type(zaxis) == hybrid_sigmap_lev_type) {
	  /* two more coord vars (a and b coeffs) */
	  ncvars+=2;
	  have_hybrid_sigmap=1;
	}
	if (pp_zaxis_lev_type(zaxis) == hybrid_height_lev_type) {
	  /* two more coord vars (a and b coeffs) */
	  ncvars+=2;
	}
      }

      /* t */
      CKI(  added = pp_list_add_or_find(taxes, &taxis, pp_genaxis_compare, 0, 
					(free_func) pp_genaxis_free,
					NULL, heaplist)  );
      if (added) {
	ncvars++;
	if (pp_taxis_is_time_mean(taxis)) {
	  /* need to make sure we have the mean dim (size 2),
	   * also one more coordinate var
	   */	  
	  have_time_mean=1;
	  ncvars++;
	}
      }

      /* associate var with these axes */
      CKI(   pp_list_add(fvar->axes,xaxis,heaplist)   );
      CKI(   pp_list_add(fvar->axes,yaxis,heaplist)   );
      CKI(   pp_list_add(fvar->axes,zaxis,heaplist)   );
      CKI(   pp_list_add(fvar->axes,taxis,heaplist)   );
      
      /* get the rotated grid, if any 
       * (NB this is done *after* the pp_list_add_or_find stuff above, because 
       * otherwise the axis pointers could get orphaned if the axes are found to 
       * be duplicates)
       */
      CKP(  fvar->rotgrid = pp_get_rotgrid(xaxis,yaxis,rotgrids,heaplist)  );

      /* add the variable */
      CKI(   pp_list_add(fieldvars, fvar, heaplist)   );
      
      /* ===================================================== */
    }
  }

    
  /*  ====================================================================
   *  Having completed the loop over records, we now know the number of
   *  dimensions and variables, so we can finally do the relevant calls
   *  to allocate these arrays and populate them usefully.
   *  ====================================================================
   */
  /* FIRST ALLOCATE THE ARRAYS, and initialise some values */
  nfvars = pp_list_size(fieldvars);

  if (nfvars <= 0) {
    CuError(CU_EOPEN,"No valid fields in file\n");
    ERR; /* not the most elegant dealing with this error - ideally would free this file */
  }
  ndims = pp_list_size(xaxes) + pp_list_size(yaxes) + pp_list_size(zaxes) + pp_list_size(taxes);

  if (have_time_mean){    
    tmdimid=ndims;
    ndims++;
  }

  if (have_hybrid_sigmap) {
    /* will need a scalar variable called "p0" with associated dimension "n1" = 1 */
    ndims++;
    ncvars++;
  }

  CKP(   cudims = CuCreateDims(file,ndims)   );

  /* need a grid_mapping variable for every rotation mapping,
   * and need lon and lat variables for every rotated grid
   */
  ncvars += pp_list_size(rotmaps) + 2*pp_list_size(rotgrids);

  nvars = ncvars + nfvars;

  CKP(   cuvars = CuCreateVars(file,nvars)   );

  for (dimid=0; dimid<ndims; dimid++) {
    dim=&cudims[dimid];
    dim->var = (CuVar*)0;
    dim->coord = (CuVar*)0;
    dim->datatype = realtype;
    dim->dimtype = CuGlobalDim;

    /* uncomment if internal structure is to be used
     *   CKP(   dim->internp = pp_malloc(sizeof(PPdim), heaplist)   );
     *   ppdim=(PPdim*)dim->internp;
     */
  }
  for (varid=0; varid<nvars; varid++) {
    var=&cuvars[varid];
    var->datatype = realtype;
    CKP(   var->internp = pp_malloc(sizeof(PPvar), heaplist)   );
    ppvar=(PPvar*)var->internp;
    ppvar->startrec=-1;
    ppvar->endrec=-1;
    ppvar->data=NULL;
    CKP(   ppvar->atts = pp_list_new(heaplist)   );
  }


  /* 
   * NOW POPULATE THE STRUCTURES
   *
   * The procedure will be to loop over all the axes, adding dimensions and
   * variables associated with those axes.
   *
   * Having done that, any dimensions not associated with axes will be added,
   * and then the field variables will be added.
   */

  dimid=0;
  varid=0;

  for (axistype=0; axistype<num_axistype; axistype++) {
    switch(axistype){
    case xaxistype: axislist=xaxes; break;
    case yaxistype: axislist=yaxes; break;
    case zaxistype: axislist=zaxes; break;
    case taxistype: axislist=taxes; break;
    default: pp_switch_bug("cdunifpp_process");
    }
    pp_list_startwalk(axislist,&handle);
    idim=0;

    while ((axis=pp_list_walk(&handle,0))!=NULL) {
      dim=&cudims[dimid];
      var=&cuvars[varid];
      ppdim=(PPdim*) dim->internp;
      ppvar=(PPvar*) var->internp;
      
      dim->coord = var;

      axis->dimid=dimid;
      dim->len=pp_genaxis_len(axis);
      CKP(  ppvar->data=pp_genaxis_getCF(axis,dimnamestem,units,ppvar->atts,heaplist)  );
      sprintf(dim->name,dimnamestem,idim);
      if (units != NULL) {
	strncpy(dim->units,units,CU_MAX_NAME);
	dim->units[CU_MAX_NAME]='\0';
      }
      strncpy(var->name,dim->name,CU_MAX_NAME);
      var->name[CU_MAX_NAME]='\0';
      var->ndims=1;
      var->dims[0] = dimid;
      varid++;
      /* now add certain variables for hybrid_sigmap z axis */
      if (axistype == zaxistype && pp_zaxis_lev_type(axis) == hybrid_sigmap_lev_type) {
      
	catts=ppvar->atts; /* attribute list for the main coord var */

	/* Hybrid sigma-p A coefficient */
	var=&cuvars[varid];
	ppvar=(PPvar*) var->internp;
	sprintf(var->name,"z%d_hybrid_sigmap_acoeff",idim);
	varnamea=var->name;
	CKP(   ppvar->data = pp_genaxis_to_values(axis,hybrid_sigmap_a_type,heaplist)   );
	CKI(   pp_add_string_att(ppvar->atts,"units","Pa",heaplist)   );
	var->ndims=1;
	var->dims[0] = dimid;
	varid++;

	/* Hybrid sigma-p B coefficient */
	var=&cuvars[varid];
	ppvar=(PPvar*) var->internp;
	sprintf(var->name,"z%d_hybrid_sigmap_bcoeff",idim);
	varnameb=var->name;
	CKP(   ppvar->data = pp_genaxis_to_values(axis,hybrid_sigmap_b_type,heaplist)   );
	var->ndims=1;
	var->dims[0] = dimid;
	varid++;
	
	snprintf(formulaterms,MAX_ATT_LEN,"ap: %s b: %s ps: ps p0: p0",varnamea,varnameb);

	CKI(   pp_add_string_att(catts,"formula_terms",formulaterms,heaplist)   );
	CKI(   pp_add_string_att(catts,"standard_name","atmosphere_hybrid_sigma_pressure_coordinate",heaplist)   );

	CKI(   pp_add_string_att(catts,"comments",
				 "The \"ps\" term in formula_terms is set to \"ps\" variable. "
				 "This variable may or may not be provided.",heaplist)   );
      }

      /* now add certain variables for hybrid_height z axis */
      if (axistype == zaxistype && pp_zaxis_lev_type(axis) == hybrid_height_lev_type) {
      
	catts=ppvar->atts; /* attribute list for the main coord var */

	/* Hybrid height A coefficient */
	var=&cuvars[varid];
	ppvar=(PPvar*) var->internp;
	sprintf(var->name,"z%d_hybrid_height_acoeff",idim);
	varnamea=var->name;
	CKP(   ppvar->data = pp_genaxis_to_values(axis,hybrid_height_a_type,heaplist)   );
	CKI(   pp_add_string_att(ppvar->atts,"units","m",heaplist)   );
	var->ndims=1;
	var->dims[0] = dimid;
	varid++;

	/* Hybrid height B coefficient */
	var=&cuvars[varid];
	ppvar=(PPvar*) var->internp;
	sprintf(var->name,"z%d_hybrid_height_bcoeff",idim);
	varnameb=var->name;
	CKP(   ppvar->data = pp_genaxis_to_values(axis,hybrid_height_b_type,heaplist)   );
	var->ndims=1;
	var->dims[0] = dimid;
	varid++;
	
	snprintf(formulaterms,MAX_ATT_LEN,"a: %s b: %s orog: orography",varnamea,varnameb);

	CKI(   pp_add_string_att(catts,"formula_terms",formulaterms,heaplist)   );
	CKI(   pp_add_string_att(catts,"standard_name","atmosphere_hybrid_sigma_pressure_coordinate",heaplist)   );

	CKI(   pp_add_string_att(catts,"comments",
				 "The \"orog\" term in formula_terms is set to \"orography\" variable. "
				 "This variable may or may not be provided.",heaplist)   );
      }


      /* add the boundary variable for time mean */
      if (axistype == taxistype && pp_taxis_is_time_mean(axis)) {
	catts=ppvar->atts; /* attribute list for the main coord var */

	var=&cuvars[varid];
	ppvar=(PPvar*) var->internp;
	sprintf(var->name,"time_bnd%d",idim);
	CKP(   ppvar->data = pp_taxis_to_boundary_values(axis->axis,heaplist)   );
	var->ndims=2;
	var->dims[0]=tmdimid;
	var->dims[1]=dimid;
	
	CKI(   pp_add_string_att(catts,"bounds",var->name,heaplist)   );

	varid++;
      }
      dimid++;
      idim++;      
    } /* end loop over axes of given */
  } /* end loop over axis types */

  /* add nv dimension if we had time mean */
  if (have_time_mean) {

    dim=&cudims[dimid];

    strcpy(dim->name,"nv");
    dim->len=2;
    
    dimid++;
  }

  /* add n1 dimension if we will be adding p0 or rotated_pole variables */
  if (have_hybrid_sigmap || pp_list_size(rotmaps) > 0) {

    dim=&cudims[dimid];
    strcpy(dim->name,"n1");
    dim->len=1;

    n1dimid=dimid;

    dimid++;    
  }


  /* add p0 variable if we had hybrid_sigmap coords */
  if (have_hybrid_sigmap) {
 
 
    var=&cuvars[varid];
    ppvar=(PPvar*) var->internp;
    sprintf(var->name,"p0");
    var->ndims=1;
    var->dims[0]=n1dimid;
    
    /* single value consisting of p0 */
    CKP(   ppvar->data = pp_data_new(realtype,1,heaplist)   );
    ((Freal*)(ppvar->data->values))[0]=reference_pressure;
    varid++;
  }

  /* add any rotated_pole variables */
  rotmapid=0;
  pp_list_startwalk(rotmaps,&handle);
  while ((rotmap=pp_list_walk(&handle,0))!=NULL) {
    
    var=&cuvars[varid];
    ppvar=(PPvar*) var->internp;
    sprintf(var->name,"rotated_pole%d",rotmapid);

    strncpy(rotmap->name,var->name,CU_MAX_NAME);
    rotmap->name[CU_MAX_NAME]='\0';

    /* single value of arbitrary type; set as integer = 0 */
    var->datatype=inttype;
    var->ndims=1;
    var->dims[0]=n1dimid;
    CKP(   ppvar->data = pp_data_new(inttype,1,heaplist)   );
    ((Freal*)(ppvar->data->values))[0]=0;

    /* and add attributes */
    catts=ppvar->atts;
    CKI(  pp_add_string_att(catts,"grid_mapping_name","rotated_latitude_longitude",heaplist)  );
    CKI(  pp_add_att(catts,"grid_north_pole_longitude",realtype,1,&rotmap->pole_lon,heaplist)  );
    CKI(  pp_add_att(catts,"grid_north_pole_latitude",realtype,1,&rotmap->pole_lat,heaplist)  );
    CKI(  pp_add_att(catts,"north_pole_grid_longitude",realtype,1,&rotmap->truepole_gridlon,heaplist)  );

    rotmapid++;
    varid++;
  }

  /* and add any lon, lat variables for rotated grids */
  rotgridid=0;
  pp_list_startwalk(rotgrids,&handle);
  while ((rotgrid=pp_list_walk(&handle,0))!=NULL) {

    lonvar=&cuvars[varid];
    lonppvar=(PPvar*) lonvar->internp;
    varid++;

    latvar=&cuvars[varid];
    latppvar=(PPvar*) latvar->internp;
    varid++;

    xaxis = rotgrid->xaxis;
    yaxis = rotgrid->yaxis;
      
    sprintf(lonvar->name,"true_lon%d",rotgridid);
    sprintf(latvar->name,"true_lat%d",rotgridid);

    sprintf(rotgrid->coords,"%s %s",lonvar->name,latvar->name);

    lonvar->ndims=2;
    latvar->ndims=2;

    lonvar->dims[0]=yaxis->dimid;
    latvar->dims[0]=yaxis->dimid;

    lonvar->dims[1]=xaxis->dimid;
    latvar->dims[1]=xaxis->dimid;

    CKI(   pp_calc_rot_grid(rotgrid,&lonppvar->data,&latppvar->data,heaplist)   );
    CKI(  pp_add_string_att(lonppvar->atts,"long_name","longitude",heaplist)  );
    CKI(  pp_add_string_att(latppvar->atts,"long_name","latitude",heaplist)  );

    CKI(  pp_add_string_att(lonppvar->atts,"standard_name","longitude",heaplist)  );
    CKI(  pp_add_string_att(latppvar->atts,"standard_name","latitude",heaplist)  );

    CKI(  pp_add_string_att(lonppvar->atts,"units","degrees_east",heaplist)  );
    CKI(  pp_add_string_att(latppvar->atts,"units","degrees_north",heaplist)  );

    CKI(  pp_add_att(lonppvar->atts,"modulo",realtype,1,&lon_modulo,heaplist)  );

    rotgridid++;
  }

  /* sanity check - the variable ID for the next variable to be added should 
   * now match the number of coordinate variables
   */
  if ( varid != ncvars ) {
    pp_error_mesg("cdunifpp_process","wrong number of coord vars?");
    ERR;
  }
  

  /* add all the attributes for coord variables
   * (didn't do inside the loop because more complicated
   * for hybrid z coords / t mean)
   */
  for (cvarid=0; cvarid<ncvars; cvarid++) {
    var=&cuvars[cvarid];
    ppvar=(PPvar*) var->internp;
    CKI(   pp_copy_and_free_atts(file,var,ppvar->atts,heaplist)   );
  }

  /*========================================================
   * Okay we've done all the variables related to dimensions
   * Add the field variables.
   *========================================================
   */
  pp_list_startwalk(fieldvars,&handle);
  while ((fvar=pp_list_walk(&handle,0))!=NULL) {
    var=&cuvars[varid];
    ppvar=(PPvar*) var->internp;
    hdrp=&ppfile->recs[fvar->startrec]->hdr;

    CKI(   pp_var_lookup(hdrp,&stashmeta)   );

    CKI(   pp_get_var_name(varid, stashmeta.shortname, cuvars)   );
    
    var->ndims=4; /* rpw axeslist len */

    idim=var->ndims;
    pp_list_startwalk(fvar->axes,&thandle);
    while ((axis=pp_list_walk(&thandle,0)) != NULL) {
      var->dims[--idim]=axis->dimid;
    }

    var->datatype=pp_get_var_type(hdrp);

    ppvar->startrec = fvar->startrec;
    ppvar->endrec = fvar->endrec;

    /* long name */
    if(strlen(stashmeta.longname)>0)
      CKI(   pp_add_string_att(ppvar->atts,"long_name",stashmeta.longname,heaplist)   );

    if(strlen(stashmeta.stdname)>0)
      CKI(   pp_add_string_att(ppvar->atts,"standard_name",stashmeta.longname,heaplist)   );

    if(strlen(stashmeta.units)>0)
	CKI(   pp_add_string_att(ppvar->atts,"units",stashmeta.units,heaplist)   );      

    if(strlen(stashmeta.source)>0)
      CKI(   pp_add_string_att(ppvar->atts,"lookup_source",stashmeta.source,heaplist)   );


    /* stash code */
    intattval = pp_get_var_stash_model(hdrp);
    CKI(   pp_add_att(ppvar->atts,"stash_model",inttype,1,&intattval,heaplist)   );
    
    intattval = pp_get_var_stash_section(hdrp);
    CKI(   pp_add_att(ppvar->atts,"stash_section",inttype,1,&intattval,heaplist)   );

    intattval = pp_get_var_stash_item(hdrp);
    CKI(   pp_add_att(ppvar->atts,"stash_item",inttype,1,&intattval,heaplist)   );

    /* fill value attribute */
    fill_ptr=pp_get_var_fill_value(hdrp);
    if(fill_ptr) {
      CKI(   pp_add_att(ppvar->atts,"_FillValue",var->datatype,1,fill_ptr,heaplist)   );
      CKI(   pp_add_att(ppvar->atts,"missing_value",var->datatype,1,fill_ptr,heaplist)   );
    }

    /* cell_methods att for time mean */

    has_cellmethod=0;
    strcpy(cellmethods,"");
    if (pp_var_is_time_mean(hdrp)) {  /* mean, min, max should be mutually exclusive */
      has_cellmethod=1;
      CKP(taxis=pp_var_get_taxis(fvar));  
      if (snprintf(cellmethods,MAX_ATT_LEN,"%s: mean",cudims[taxis->dimid].name) > MAX_ATT_LEN+1) {
	cellmethods[MAX_ATT_LEN]='\0';
      }
    }
    if (pp_var_is_time_max(hdrp)) {
      has_cellmethod=1;
      CKP(taxis=pp_var_get_taxis(fvar));
      if (snprintf(cellmethods,MAX_ATT_LEN,"%s: maximum",cudims[taxis->dimid].name) > MAX_ATT_LEN+1) {
	cellmethods[MAX_ATT_LEN]='\0';
      }
    }
    if (pp_var_is_time_min(hdrp)) {
      has_cellmethod=1;
      CKP (taxis=pp_var_get_taxis(fvar));
      if (snprintf(cellmethods,MAX_ATT_LEN,"%s: minimum",cudims[taxis->dimid].name) >MAX_ATT_LEN+1) {
	cellmethods[MAX_ATT_LEN]='\0';
      }
    }
    if (pp_var_is_zonal_mean(hdrp)) {
      has_cellmethod=1;
      CKP(xaxis=pp_var_get_xaxis(fvar));;
      if (snprintf(tmpstring,MAX_ATT_LEN," %s: mean",cudims[xaxis->dimid].name) > MAX_ATT_LEN+1) {
	tmpstring[MAX_ATT_LEN]='\0';
      }
      ilen1=strlen(cellmethods);
      ilen2=strlen(tmpstring);
      strncat(cellmethods,tmpstring,MAX_ATT_LEN-ilen1);  /* correct length? */
      if ((ilen1+ilen2) > MAX_ATT_LEN+1) {
	cellmethods[MAX_ATT_LEN]='\0';
      }
    }
    if (has_cellmethod) {
      CKI(   pp_add_string_att(ppvar->atts,"cell_methods",cellmethods,heaplist)   );
    }

    /* rotated grid mapping (if any) */
    if (fvar->rotgrid != NON_ROTATED_GRID) {

      CKI(   pp_add_string_att(ppvar->atts,"grid_mapping",fvar->rotgrid->rotmap->name,heaplist)   );
      CKI(   pp_add_string_att(ppvar->atts,"coordinates",fvar->rotgrid->coords,heaplist)   );
    }

    /* add supervar attribute */
    svindex=ppfile->recs[fvar->startrec]->supervar_index;
    if (svindex >= 0) {
      CKI(   pp_add_att(ppvar->atts,"super_variable_index",inttype,1,&svindex,heaplist)   );
    }

    /* FIXME(?): maybe do time difference analogously to time mean, but with different
     * cell_methods attribute.  See also pp_taxis_to_values() in cdunifpp_axisvals.c
     */
   
    CKI(   pp_copy_and_free_atts(file,var,ppvar->atts,heaplist)   );

    varid++;
  }

  /* sanity check - the variable ID for the next variable to be added (if there was one,
   * which there isn't), should now match the total number of variables
   */
  if ( varid != nvars ) {
    pp_error_mesg("cdunifpp_process","wrong number of vars?");
    ERR;
  }

  /*========================================================
   * All done and ready for dimget / varget.
   * Free up some of the most important temporary
   * heap variables.
   *========================================================
   */

  /* free all the axes */
  /* JAK when do more general x,y axes will need to worry about
   * freeing x and y axes values too
   */
  pp_list_startwalk(zaxes,&handle);
  while ((zaxis=pp_list_walk(&handle,0))!=NULL) {
    CKI(   pp_genaxis_free(zaxis,heaplist)   );
  }
  pp_list_startwalk(taxes,&handle);
  while ((taxis=pp_list_walk(&handle,0))!=NULL) {
    CKI(   pp_genaxis_free(taxis,heaplist)   );
  }
  CKI(   pp_list_free(xaxes,1,heaplist)   );
  CKI(   pp_list_free(yaxes,1,heaplist)   );
  CKI(   pp_list_free(zaxes,0,heaplist)   );
  CKI(   pp_list_free(taxes,0,heaplist)   );

  /* free all the field vars */ 
  pp_list_startwalk(fieldvars,&handle);
  while ((fvar=pp_list_walk(&handle,0))!=NULL) {
    CKI(   pp_list_free(fvar->axes,0,heaplist)   );
  }
  CKI(   pp_list_free(fieldvars,1,heaplist)   );
  
  /* set numbers in file structure */
  file->ndims=ndims;
  file->nvars=nvars;
  file->recdim=-1;

  /* global attributes: */

  CKI(   pp_add_string_att(gatts,"history","PP/UM file read by cdunif",heaplist)   );

  /*-------------------------*/
  /* input_uri */
  if (file->controlpath[0]=='/') {
    snprintf(input_uri,MAX_ATT_LEN,"file://%s",file->controlpath);
  }
  else {
    if(getcwd(current_directory,MAX_ATT_LEN)!=NULL) {
      snprintf(input_uri,MAX_ATT_LEN,"file://%s/%s",current_directory,file->controlpath);
    } else {
      /* better than nothing */
      snprintf(input_uri,MAX_ATT_LEN,"%s",file->controlpath);
    }
  }
  input_uri[MAX_ATT_LEN]='\0';
  CKI(   pp_add_string_att(gatts,"input_uri",input_uri,heaplist)   );
  /*-------------------------*/

  intattval=ppfile->wordsize;
  CKI(   pp_add_att(gatts,"input_word_length",inttype,1,&intattval,heaplist)   );

#ifdef LITTLE_ENDIAN_MACHINE
  bigend = ppfile->swap;
#else
  bigend = !ppfile->swap;
#endif

  CKI(   pp_add_string_att(gatts,"input_byte_ordering", 
			   bigend ? "big_endian" : "little_endian", heaplist)   );

  if (ppfile->type == um_type)
    CKI(   pp_add_string_att(gatts,"input_file_format","UM ancillary",heaplist)   );

  if (ppfile->type == pp_type)
    CKI(   pp_add_string_att(gatts,"input_file_format","PP",heaplist)   );

  /* add global attributes */
  CKI(   pp_copy_and_free_atts(file,NULL,gatts,heaplist)   );

  return 0;

  ERRBLKI("cdunifpp_process");
}

#endif
