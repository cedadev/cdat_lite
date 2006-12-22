import genutil,MV


a=MV.array([1,2,3,4,5],mask=[0,0,1,0,0])


print genutil.statistics.std(a)
print genutil.statistics.std(a,max_pct_missing=80.)
print genutil.statistics.std(a,max_pct_missing=79)
