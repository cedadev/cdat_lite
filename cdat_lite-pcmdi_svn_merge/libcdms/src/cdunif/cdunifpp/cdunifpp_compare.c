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
 * COMPARISON FUNCTIONS.
 *
 * NOTE: functions which take arguments of type void* (except for pp_compare_ptrs)
 *   are designed to be used with generic routines:
 *   pp_compare_records is envisaged for use with qsort;
 *   several other functions are envisaged for use with pp_compare_lists (below).
 *
 *   In these cases if supplying pointers directly to the relevant structures, need to generate
 *   an extra level of pointer with "&" syntax.
 *
 * But not all functions below are like that.  Don't assume functions can be used analogously
 * without first examining the argument lists.
 */

/* The code profiler suggests that pp_compare_ints and pp_compare_reals are candidates for
 * inlining; however, unfortunately this sometimes gets compiled with c89 which doesn't support
 * inline functions.  Use a #define for pp_compare_ints.  pp_compare_reals, which is more
 * awkward to #define, is just going to have to stay as it is for now (it's called less often).
 */

/* Now included in cdunifpp.h
 * #define pp_compare_ints(a,b) ((a)<(b)?(-1):(a)>(b)?1:0)
 */

/*
 * static int pp_compare_ints(Fint a, Fint b)
 * {
 *   if (a<b) return -1;
 *   if (a>b) return 1;
 *   return 0;
 * }
 */

static int pp_compare_reals(Freal a, Freal b)
{
  Freal delta;

  /* first test for special case (unnecessary, but code profiler shows 
   * slightly more efficient)
   */
  if (a==b) return 0;

  delta = fabs(b * tolerance);
  if (a<b-delta) return -1;
  if (a>b+delta) return 1;

  return 0;
}

/* compares two pointers - not in an intelligent way, but
 * just checks if they point to same memory, and if not then
 * returns +1 or -1 which will give a (pretty arbitrary) ordering
 */

static int pp_compare_ptrs(const void *a, const void *b)
{
  if (a<b) return -1;
  if (a>b) return 1;
  return 0;
}


/* routine to compare two PP records.
 * returns: 
 *    -2 or 2  headers are from different variable
 *    -1 or 1  headers are from same variable
 *       0     difference not found in elements inspected
 */

int pp_compare_records(const void *p1, const void *p2)
{
  const PPrec *a = *(PPrec **)p1;
  const PPrec *b = *(PPrec **)p2;

#define COMPARE_INTS(tag,ret) {int cmp=pp_compare_ints(a->hdr.tag,b->hdr.tag); if (cmp!=0) return cmp*(ret);}
#define COMPARE_REALS(tag,ret) {int cmp=pp_compare_reals(a->hdr.tag,b->hdr.tag); if (cmp!=0) return cmp*(ret);}

  /* elements to distinguish variables */

  COMPARE_INTS(LBUSER4,2);
  COMPARE_INTS(LBUSER7,2);
  COMPARE_INTS(LBCODE,2);
  COMPARE_INTS(LBVC,2);
  COMPARE_INTS(LBTIM,2);
  COMPARE_INTS(LBPROC,2);
  COMPARE_REALS(BPLAT,2);
  COMPARE_REALS(BPLON,2);
  COMPARE_INTS(LBHEM,2);
  COMPARE_INTS(LBROW,2);
  COMPARE_INTS(LBNPT,2);

  COMPARE_REALS(BGOR,2);
  COMPARE_REALS(BZY,2);
  COMPARE_REALS(BDY,2);
  COMPARE_REALS(BZX,2);
  COMPARE_REALS(BDX,2);

  /* Disambig index is used to force distinction between variables for records whose headers
   * are the same.  It is initialised to the same value for all records (in fact -1), but may
   * later be set to different values according to some heuristic.
   */

  {
    int cmp=pp_compare_ints(a->disambig_index,b->disambig_index);
    if (cmp!=0) return cmp*2;
  }

  /* elements to sort records within a variable
   * (sort on time, then sort on level)
   */

  COMPARE_INTS(LBFT,1);

  COMPARE_INTS(LBYR,1);
  COMPARE_INTS(LBMON,1);
  COMPARE_INTS(LBDAT,1);
  COMPARE_INTS(LBDAY,1);
  COMPARE_INTS(LBHR,1);
  COMPARE_INTS(LBMIN,1);

  COMPARE_INTS(LBYRD,1);
  COMPARE_INTS(LBMOND,1);
  COMPARE_INTS(LBDATD,1);
  COMPARE_INTS(LBDAYD,1);
  COMPARE_INTS(LBHRD,1);
  COMPARE_INTS(LBMIND,1);

  COMPARE_INTS(LBLEV,1);
  COMPARE_REALS(BLEV,1);
  COMPARE_REALS(BHLEV,1);

  return 0;
}

int pp_records_from_different_vars(const PPrec *a, const PPrec *b)
{
  int cmp;
  cmp = pp_compare_records(&a,&b);
  if (cmp == -2) return 1;
  if (cmp == 2) return 1;
  return 0;
}

/*---------------------------------------------------------*/

int pp_compare_regaxes(const void *p1, const void *p2) {

  const PPregaxis *a = *(PPregaxis **)p1;
  const PPregaxis *b = *(PPregaxis **)p2;
  int cmp;
  if ((cmp=pp_compare_ints(a->n,b->n))!=0) return cmp;
  if ((cmp=pp_compare_reals(a->start,b->start))!=0) return cmp;
  if ((cmp=pp_compare_reals(a->interval,b->interval))!=0) return cmp;
  if ((cmp=pp_compare_rotmaps(&a->rotmap,&b->rotmap))!=0) return cmp;
  
  return 0;
}

int pp_compare_rotmaps( const void *p1, const void *p2 ) {

  const PProtmap *a = *(PProtmap **)p1;
  const PProtmap *b = *(PProtmap **)p2;
  int cmp;
  if (a == NON_ROTATED || b==NON_ROTATED)
    return pp_compare_ptrs(a,b);

  else {
    if ((cmp=pp_compare_reals(a->pole_lon,b->pole_lon))!=0) return cmp;
    if ((cmp=pp_compare_reals(a->pole_lat,b->pole_lat))!=0) return cmp;
    if ((cmp=pp_compare_reals(a->truepole_gridlon,b->truepole_gridlon))!=0) return cmp;
    return 0;
  }
}

int pp_compare_rotgrids( const void *p1, const void *p2 ) {

  const PProtgrid *a = *(PProtgrid **)p1;
  const PProtgrid *b = *(PProtgrid **)p2;
  int cmp;

  /* use comparison functions which compare the actual elements --
   * but this may be overkill, we could use pp_compare_ptr instead
   * in these 3 lines
   */

  if ((cmp=pp_compare_rotmaps(&a->rotmap,&b->rotmap))!=0) return cmp;
  if ((cmp=pp_genaxis_compare(&a->xaxis,&b->xaxis))!=0) return cmp;
  if ((cmp=pp_genaxis_compare(&a->yaxis,&b->yaxis))!=0) return cmp;
  return 0;
}


int pp_compare_xsaxes( const void *p1, const void *p2 ) {
  const PPxsaxis *a = *(PPxsaxis **)p1;
  const PPxsaxis *b = *(PPxsaxis **)p2;
  int cmp;
  int i;
  Freal *values1, *values2;

  if ((cmp=pp_compare_ints(a->data->n, b->data->n)) != 0) return cmp;

  values1=(Freal *) a->data->values;
  values2=(Freal *) b->data->values;

  for (i=0; i< a->data->n; i++) {
    if ((cmp=pp_compare_reals(values1[i], values2[i])) !=0 ) return cmp;
  }
  return 0;
}

int pp_compare_lists(const PPlist *l1, const PPlist *l2, int (*compfunc)(const void*, const void*)) {
  int i,n,cmp;
  const void *item1, *item2;
  PPlisthandle handle1, handle2;

  /* differ if number of items differs */
  n=pp_list_size(l1);
  if ((cmp=pp_compare_ints(n,pp_list_size(l2)))!=0) return cmp;
  
  /* differ if any individual item differs */
  pp_list_startwalk(l1,&handle1);
  pp_list_startwalk(l2,&handle2);
  for (i=0; i<n; i++) {
    item1=pp_list_walk(&handle1,0);
    item2=pp_list_walk(&handle2,0);
    if ((cmp=compfunc(&item1,&item2))!=0) return cmp;
  }
  return 0;
}

int pp_compare_levels(const void *p1, const void *p2) {
  const PPlevel *a = *(PPlevel **)p1;
  const PPlevel *b = *(PPlevel **)p2;
  int cmp;

  /* macros called LCOMPARE_INTS and LCOMPARE_REALS to emphasise difference from those in pp_compare_records */

#define LCOMPARE_INTS(tag) {int cmp=pp_compare_ints(a->tag,b->tag); if (cmp!=0) return cmp;}
#define LCOMPARE_REALS(tag) {int cmp=pp_compare_reals(a->tag,b->tag); if (cmp!=0) return cmp;}

  LCOMPARE_INTS(type);

  switch (a->type) {
  case hybrid_height_lev_type:
    LCOMPARE_REALS(values.hybrid_height.a);
    LCOMPARE_REALS(values.hybrid_height.b);
#ifdef BDY_LEVS
    LCOMPARE_REALS(values.hybrid_height.ubdy_a);
    LCOMPARE_REALS(values.hybrid_height.ubdy_b);
    LCOMPARE_REALS(values.hybrid_height.lbdy_a);
    LCOMPARE_REALS(values.hybrid_height.lbdy_b);
#endif
    break;
  case hybrid_sigmap_lev_type:
    LCOMPARE_REALS(values.hybrid_sigmap.a);
    LCOMPARE_REALS(values.hybrid_sigmap.b);
#ifdef BDY_LEVS
    LCOMPARE_REALS(values.hybrid_sigmap.ubdy_a);
    LCOMPARE_REALS(values.hybrid_sigmap.ubdy_b);
    LCOMPARE_REALS(values.hybrid_sigmap.lbdy_a);
    LCOMPARE_REALS(values.hybrid_sigmap.lbdy_b);
#endif
    break;
  case pseudo_lev_type:
    LCOMPARE_INTS(values.pseudo.index);
    break;
  default:
    LCOMPARE_REALS(values.misc.level);
#ifdef BDY_LEVS
    LCOMPARE_REALS(values.misc.ubdy_level);
    LCOMPARE_REALS(values.misc.lbdy_level);
#endif
    break;
  }
  return 0;
}

int pp_compare_zaxes(const void *p1, const void *p2) {
  const PPzaxis *a = *(PPzaxis **)p1;
  const PPzaxis *b = *(PPzaxis **)p2;
  int cmp;
  /* differ if level type differs */
  /*   if ((cmp=pp_compare_ints(a->type,b->type))!=0) return cmp;  */
  /* differ if level lists differ */
  if ((cmp=pp_compare_lists(a->values,b->values,pp_compare_levels))!=0) return cmp;
  return 0;
}

int pp_compare_times(const void *p1, const void *p2) {
  const PPtime *a = *(PPtime **)p1;
  const PPtime *b = *(PPtime **)p2;
  int cmp;

  /* LBTYP: ignore 100s digit = sampling frequency, as we don't use it for anything */
  if ((cmp=pp_compare_ints(a->type%100,b->type%100))!=0) return cmp;

  if ((cmp=pp_compare_dates(&a->time1,&b->time1))!=0) return cmp;
  if ((cmp=pp_compare_dates(&a->time2,&b->time2))!=0) return cmp;
  return 0;
}

int pp_compare_dates(const PPdate *a, const PPdate *b) {
  int cmp;
  if ((cmp=pp_compare_ints(a->year  ,b->year  ))!=0) return cmp;
  if ((cmp=pp_compare_ints(a->month ,b->month ))!=0) return cmp;
  if ((cmp=pp_compare_ints(a->day   ,b->day   ))!=0) return cmp;
  if ((cmp=pp_compare_ints(a->hour  ,b->hour  ))!=0) return cmp;
  if ((cmp=pp_compare_ints(a->minute,b->minute))!=0) return cmp;
  if ((cmp=pp_compare_ints(a->second,b->second))!=0) return cmp;
  return 0;
}

int pp_compare_taxes(const void *p1, const void *p2) {
  const PPtaxis *a = *(PPtaxis **)p1;
  const PPtaxis *b = *(PPtaxis **)p2;
  int cmp;
  /* differ if time type differs */
  /*  if ((cmp=pp_compare_ints(a->type%100,b->type%100))!=0) return cmp;  */

  /* differ if time origin differs */
  if ((cmp=pp_compare_dates(&a->time_orig,&b->time_orig))!=0) return cmp;

  /* differ if time lists differ */
  if ((cmp=pp_compare_lists(a->values,b->values,pp_compare_times))!=0) return cmp;
  return 0;
}

#endif
