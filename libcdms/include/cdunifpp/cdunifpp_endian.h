/*---------------------------------------------------------*/

/* endian-ness - set or clear LITTLE__ENDIAN *
 * currently seems that BYTESWAP is set for us, so use that,
 * but could change to include endian.h and then
 * test using #if (__BYTE_ORDER == __LITTLE_ENDIAN)
 */
#if __BYTE_ORDER == __LITTLE_ENDIAN
#define LITTLE__ENDIAN
#undef BIG__ENDIAN
#else
#define BIG__ENDIAN
#undef LITTLE__ENDIAN
#endif

/*---------------------------------------------------------*/
