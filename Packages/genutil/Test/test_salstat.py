import Numeric,MA,genutil,sys,math,MV
import salstat_stats

for M in [MA,MV]:
    print 'Testing with ',M
    for axis in [0,1]:
        print 'Testing axis:',axis
        
        a=[1,2,3,4,5,67]
        b=[5,7,2,5,87,3,4,7,4,23,7,9,5]

        A=M.array(a)
        B=M.array(b)
        C=M.array([b,b])
        if axis==0:
            C=M.transpose(C)
        print 'Salstat:',salstat_stats.tiecorrect(b)
        print genutil.salstat.tiecorrect(C,axis=axis)

        print 'Testing ZPROB'
        Z=[0.,-17,17,-.5,.5,-4,4,-math.sqrt(50),50]
        sal=[]
        for z in Z:
            sal.append(salstat_stats.zprob(z))
        Z=M.array([Z,Z])
        if axis==0:
            Z=M.transpose(Z)
        res2 = genutil.salstat.zprob(Z)
        if axis==0:
            t=res2[:,0]
        else:
            t=res2[0]
        if M.allequal(M.array(sal),t):
            print 'ZPROB ok !'
        else:
            raise 'Error with Zprob !'+str(sal)+str(t)

        print 'Testing chisqprob'
        chisq = [-4., 1. , 4., 4., 50., 50., 12., 12.,]
        df    = [ 1.,  .2, 1., 2.,  4.,  5.,  4. , 5., ]

        Chisq=M.array(chisq)
        Df=M.array(df)

        CC=M.array([chisq,chisq])
        DDf=M.array([df,df])
        if axis==0:
            CC=M.transpose(CC)
            DDf=M.transpose(DDf)

        sal=[]
        for i in range(len(chisq)):
            c=chisq[i]
            d=df[i]
            sal.append(salstat_stats.chisqprob(c,d))
        res2 = genutil.salstat.chisqprob(CC,DDf)

        if axis==0:
            t=res2[:,0]
        else:
            t=res2[0]
        if M.allequal(M.array(sal),t):
            print 'chisqprob ok !'
        else:
            raise 'Error with chisqprob !',sal,t

        print 'Testing InverseChi'
        prob = [ -1, 0, 1, 1.2, .1, .2, .3, .4, .5, .6, .7, .8, .9, ]
        df = range(3,3+len(prob))
        sal=[]
        for i in range(len(df)):
            p,d=prob[i],df[i]
            sal.append(salstat_stats.inversechi(p,d))
        Prob=M.array([prob,prob])
        Df=M.array([df,df])
        if axis==0:
            Prob=M.transpose(Prob)
            Df=M.transpose(Df)

        res2 = genutil.salstat.inversechi(Prob,Df)
        if axis==0:
            t=res2[:,0]
        else:
            t=res2[0]
        if M.allequal(M.array(sal),t):
            print 'InverseChi ok !'
        else:
            raise 'Error with InverseChi !'+str(sal)+str(t)

        print 'Testing erfcc'
        df = M.arange(-5,5,.5)
        sal=[]
        for i in range(len(df)):
            x=float(df[i])
            sal.append(salstat_stats.erfcc(x))
        Df=M.resize(df,(2,df.shape[0]))
        if axis==0:
            Df=M.transpose(Df)

        r = genutil.salstat.erfcc(Df)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'erfcc ok !'
        else:
            raise 'Error with erfcc !'+str(sal)+str(t)

        print 'Testing ksprob'
        df = M.arange(-5,5,2)
        sal=[]
        for i in range(len(df)):
            x=float(df[i])
            sal.append(salstat_stats.ksprob(x))
        Df=M.resize(df,(2,df.shape[0]))
        if axis==0:
            Df=M.transpose(Df)

        r=genutil.salstat.ksprob(Df)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'ksprob ok !'
        else:
            raise 'Error with ksprob !'+str(sal)+str(t)

        print 'Testing betacf'
        a = MA.arange(.1,5,.02)
        b = a*.1+.5
        X= a*.005+.5
        sal=[]
        for i in range(len(X)):
            sal.append(salstat_stats.betacf(a[i],b[i],X[i]))
        A=M.resize(a,(2,a.shape[0]))
        B=M.resize(b,(2,b.shape[0]))
        X=M.resize(X,(2,X.shape[0]))
        if axis==0:
            A=M.transpose(A)
            B=M.transpose(B)
            X=M.transpose(X)
        r=genutil.salstat.betacf(A,B,X)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'betacf ok !'
        else:
            raise 'Error with betacf !\n'#+str(sal)+'\n'+str(t)+'\n'+str(M.array(sal)-t)

        print 'Testing gammaln'
        df = M.arange(0.1,500,.2)
        sal=[]
        for i in range(len(df)):
            x=float(df[i])
            sal.append(salstat_stats.gammln(x))
        Df=M.resize(df,(2,df.shape[0]))
        if axis==0:
            Df=M.transpose(Df)

        r=genutil.salstat.gamma(Df)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'gammaln ok !'
        else:
            raise 'Error with gammaln !'+str(sal)+str(t)

        print 'Testing betai'
        X = M.arange(.001,1,.04)
        a= X*.005+.5
        b = a*.1+.5
        sal=[]
        for i in range(len(X)):
            sal.append(salstat_stats.betai(a[i],b[i],X[i]))
        A=M.resize(a,(2,a.shape[0]))
        B=M.resize(b,(2,b.shape[0]))
        X=M.resize(X,(2,X.shape[0]))
        if axis==0:
            A=M.transpose(A)
            B=M.transpose(B)
            X=M.transpose(X)
        r=genutil.salstat.betai(A,B,X)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'betai ok !'
        else:
            raise 'Error with betai !'+str(sal)+str(t)

        print 'Testing fprob'
        a = M.arange(.1,5,.02)
        b = a*.1+.5
        X= a*.005+.5
        sal=[]
        for i in range(len(X)):
            sal.append(salstat_stats.fprob(a[i],b[i],X[i]))
        A=M.resize(a,(2,a.shape[0]))
        B=M.resize(b,(2,b.shape[0]))
        X=M.resize(X,(2,X.shape[0]))
        if axis==0:
            A=M.transpose(A)
            B=M.transpose(B)
            X=M.transpose(X)
        r=genutil.salstat.fprob(A,B,X)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'fprob ok !'
        else:
            raise 'Error with fprob !'+str(sal)+str(t)

        print 'Testing tprob'
        a = M.arange(.1,5,.02)
        b = a*.1+.5
        X= a*.005+.5
        sal=[]
        for i in range(len(X)):
            sal.append(salstat_stats.tprob(a[i],b[i]))
        A=M.resize(a,(2,a.shape[0]))
        B=M.resize(b,(2,b.shape[0]))
        X=M.resize(X,(2,X.shape[0]))
        if axis==0:
            A=M.transpose(A)
            B=M.transpose(B)
            X=M.transpose(X)
        r=genutil.salstat.tprob(A,B)

        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'tprob ok !'
        else:
            raise 'Error with tprob !'+str(sal)+str(t)

        print 'Testing inversef'
        prob = M.arange(0.,1,.1)
        df1=range(1,len(prob)+1)
        df2=range(100,100+len(prob))
        sal=[]
        for i in range(len(df2)):
            sal.append(salstat_stats.inversef(prob[i],df1[i],df2[i]))
        A=M.resize(prob,(2,prob.shape[0]))
        B=M.array([df1,df1])
        X=M.array([df2,df2])
        if axis==0:
            A=M.transpose(A)
            B=M.transpose(B)
            X=M.transpose(X)
        r=genutil.salstat.inversef(A,B,X)
        if axis==0:
            t=r[:,0]
        else:
            t=r[0]
        if M.allequal(M.array(sal),t):
            print 'inversef ok !'
        else:
            raise 'Error with inversef !'+str(sal)+':'+str(t)


        inlist=[4, 5, 6, 2, 3, 3, 3, 3, 3, 3, 4, 5, 2, 1, 7, 8, 9]
        Inlist=M.array([inlist,inlist])
        if axis==0:
            Inlist=M.transpose(Inlist)

        print '\nFullDescriptive\n'
        FD=salstat_stats.FullDescriptives(inlist)
        for op in ['sumsquares','Range','harmmean','median','medianranks','mad',
                   'numberuniques','ssdevs','geomean','samplevar','variance','stddev','coeffvar',
                   'skewness','kurtosis','stderr','mode',
                   ]:
            print 'Testing:',op
            sal=M.array(getattr(FD,op.lower()))
            ## Converts names
            if op=='harmmean' : op='harmonicmean'
            if op=='geomean' : op='geometricmean'
            if op=='stddev' : op='standarddeviation'
            if op=='coeffvar' : op='coefficentvariance'
            if op=='stderr' : op='standarderror'
            if op=='samplevar' : op='unbiasedvariance'
            exec('r=genutil.salstat.'+op+'(Inlist,axis=axis)')
            if isinstance(sal,list):
                if M.allequal(M.array(sal),r[:,0]):
                    print op+' ok !'
                else:
                    raise 'Error with '+op+' !\n'+str(sal)+'\n'+str(r[:,0])
            else:
                if M.allequal(M.array(sal),r[0]):
                    print op+' ok !'
                else:
                    raise 'Error with '+op+' !\n'+str(sal)+'\n'+str(r[0])

        print '\nOneSample Test\n'
        inlist2=[14, .5, 16, 22, 13.0, .3, 43, 32, 13, 13, .4, 5.5, 2.2, 11, 27, 5.8, 19]
        Inlist2=M.array([inlist2,inlist2])
        if axis==0:
            Inlist2=M.transpose(Inlist2)
        userval=4.27
        Userval=M.array([userval,userval])

##         Initialize salstat stuff
        OS=salstat_stats.OneSampleTests(inlist)

        print 'Testing OneSampleTTest'
        OS.OneSampleTTest(userval)
        t,prob=genutil.salstat.OneSampleTTest(Inlist,Userval,axis=axis,df=0)
        if OS.t!=t[0] or OS.prob!=prob[0]:
            raise 'Error with OneSampleTests !'+str(OS.t)+'\n'+str(OS.prob)+'\n'+str(t[0])+'\n'+str(prob[0])
        else:
            print 'OneSampleTTest ok'

        print 'Testing OneSampleSignTest'
        OS.OneSampleSignTest(inlist,userval)
        nplus,nminus,ntotal,z,prob=genutil.salstat.OneSampleSignTest(Inlist,Userval,axis=axis)
        if OS.z!=z[0] or OS.nminus!=nminus[0] or OS.nplus!=nplus[0] or OS.ntotal!=ntotal[0]:
            print 'Error with OneSampleSignTest'
            print 'Plus:',OS.nplus,nplus[0]
            print 'MMinus',OS.nminus,nminus[0]
            print 'Ntotal:',OS.ntotal,ntotal[0]
            print 'Z:',OS.z,z[0]
            print 'prob:',OS.prob,prob[0]
            raise ''
        else:
            print 'OneSampleSignTest ok'
        print 'Testing ChiSquareVariance'
        OS.ChiSquareVariance(userval)
        chi,prob=genutil.salstat.ChiSquareVariance(Inlist,Userval,axis=axis,df=0)
        if OS.chisquare!=chi[0] or OS.prob!=prob[0]:
            raise 'Error with ChiSquareVariance !'+str(OS.chisquare)+'\n'+str(OS.prob)+'\n'+str(chi[0])+'\n'+str(prob[0])
        else:
            print 'ChiSquareVariance ok'


        print '\nTwoSample Tests\n'
        TS=salstat_stats.TwoSampleTests(inlist,inlist2)

        print 'TTestUnpaired'
        TS.TTestUnpaired()
        t,prob=genutil.salstat.TTestUnpaired(Inlist,Inlist2,axis=axis,df=0)
        if TS.t!=t[0] or TS.prob!=prob[0]:
            raise 'Error TTestUnpaired  !'+str(TS.t)+'\n'+str(TS.prob)+'\n'+str(t[0])+'\n'+str(prob[0])
        else:
            print 'TTestUnpaired ok'

        print 'Paired'
        TS.TTestPaired(inlist,inlist2)
        t,prob=genutil.salstat.TTestPaired(Inlist,Inlist2,axis=axis,df=0)
        if TS.t!=t[0] or TS.prob!=prob[0]:
            raise 'Error TTestPaired !'+str(TS.t)+'\n'+str(TS.prob)+'\n'+str(t[0])+'\n'+str(prob[0])
        else:
            print 'TTestPaired ok'

        print 'PearsonCorrel'
        TS.PearsonsCorrelation(inlist,inlist2)
        r, t, prob=genutil.salstat.PearsonsCorrelation(Inlist,Inlist2,axis=axis,df=0)
        if TS.t!=t[0] or  TS.r!=r[0] or TS.prob!=prob[0]:
            print 'Error PearsonCorrel !'
            print TS.r,r[0]
            print TS.t,t[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'PearsonCorrel ok'

        print 'Ftest'
        TS.FTest(.0300)
        t,prob=genutil.salstat.FTest(Inlist,Inlist2,M.array([.03,.03]),axis=axis,df=0)
        if TS.f!=t[0] or TS.prob!=prob[0]:
            raise 'Error FTest !'+str(TS.f)+'\n'+str(TS.prob)+'\n'+str(t[0])+'\n'+str(prob[0])
        else:
            print 'FTest ok'

        print 'TwoSampleSignTest'
        TS.TwoSampleSignTest(inlist,inlist2)
        nplus,nminus,ntotal,z,prob=genutil.salstat.TwoSampleSignTest(Inlist,Inlist2,axis=axis)

        if TS.nplus!=nplus[0] or TS.nminus!=nminus[0] or TS.ntotal!=ntotal[0] or TS.z!=z[0]:
            print 'Error TwoSampleSignTest !'
            print TS.nplus,nplus[0]
            print TS.nminus,nminus[0]
            print TS.ntotal,ntotal[0]
            print TS.z,z[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'TwoSampleSignTest ok'

        print 'KendallsTau'
        TS.KendallsTau(inlist,inlist2)
        tau,z,prob=genutil.salstat.KendallsTau(Inlist,Inlist2,axis=axis)
        if TS.nplus!=nplus[0] or TS.nminus!=nminus[0] \
               or TS.ntotal!=ntotal[0] or TS.z!=z[0]:
            print TS.tau,tau[0]
            print TS.z,z[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'KendallsTau ok'

        print 'KolmogorovSmirnov'
        TS.KolmogorovSmirnov()
        d,prob=genutil.salstat.KolmogorovSmirnov(Inlist,Inlist2,axis=axis)
        if TS.d!=d[0] or TS.prob!=prob[0]:
            print 'Error KolmogorovSmirnov!'
            print TS.d,d[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'KolmogorovSmirnov ok'

        print 'SpearmansCorrelation'
        TS.SpearmansCorrelation(inlist,inlist2)
        rho,t,prob=genutil.salstat.SpearmansCorrelation(Inlist,Inlist2,axis=axis,df=0)
        if TS.t!=t[0] or TS.prob!=prob[0] or TS.rho!=rho[0]:
            print 'Error SpearmansCorrelation !'
            print TS.rho,rho[0]
            print TS.t,t[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'SpearmansCorrelation ok'

        print 'RankSums'
        TS.RankSums(inlist,inlist2)
        z,prob=genutil.salstat.WilcoxonRankSums(Inlist,Inlist2,axis=axis)
        if TS.d!=d[0] or TS.prob!=prob[0]:
            print 'Error  WilcoxonRankSums!'
            print TS.z,z[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print ' WilcoxonRankSums ok'

        print 'SignedRanks'
        TS.SignedRanks(inlist,inlist2)
        wt,z,prob=genutil.salstat.WilcoxonSignedRanks(Inlist,Inlist2,axis=axis)
        if TS.z!=z[0] or TS.prob!=prob[0] or TS.wt!=wt[0]:
            print 'Error  WilcoxonSignedRanks !'
            print TS.wt,wt[0]
            print TS.z,z[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'WilcoxonSignedRanks ok'

        print 'MannWhitneyU'
        TS.MannWhitneyU(inlist,inlist2)
        bigu,smallu,z,prob=genutil.salstat.MannWhitneyU(Inlist,Inlist2,axis=axis)
        if TS.bigu!=bigu[0] or TS.smallu!=smallu[0] or TS.prob!=prob[0] or TS.z!=z[0]:
            print 'Error MannWhitneyU !'
            print TS.bigu,bigu[0]
            print TS.smallu,smallu[0]
            print TS.z,z[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'MannWhitneyU ok'

        print 'LinearRegression'
        TS.LinearRegression(inlist,inlist2)
        r,t,prob,slope,intercept,sterrtest=genutil.salstat.LinearRegression(Inlist,Inlist2,axis=axis,df=0)
        if TS.r!=r[0] or TS.t!=t[0] or TS.slope!=slope[0] or TS.intercept!=intercept[0]\
               or TS.sterrest!=sterrtest[0] or TS.prob!=prob[0]:
            print 'Error  LinearRegression!'
            print TS.r,r[0]
            print TS.t,t[0]
            print TS.slope,slope[0]
            print TS.intercept,intercept[0]
            print TS.sterrest,sterrtest[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'LinearRegression ok'

        ## ## HIS seem to not work !
        ## print 'PairedPermutation'
        ## TS.PairedPermutation(inlist,inlist2)
        ## utail,crit,prob=genutil.salstat.PairedPermutation(Inlist,Inlist2)
        ## if TS.utail!=utail[0] or TS.crit!=crit[0] or TS.prob!=prob[0]:
        ##     print 'Error PairedPermutation !'
        ##     print TS.utail,utail[0]
        ##     print TS.crit,crit[0]
        ##     print TS.prob,prob[0]
        ##     raise ''
        ## else:
        ##     print 'PairedPermutation ok'

        print 'ChiSquare'
        TS.ChiSquare(inlist,inlist2)
        chisq,prob=genutil.salstat.ChiSquare(Inlist,Inlist2,axis=axis,df=0)
        if TS.chisq!=chisq[0] or TS.prob!=prob[0]:
            print 'Error ChiSquare !'
            print TS.chisq,chisq[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'ChiSquare ok'

        print '\nMulti sample Tests\n'
        TS=salstat_stats.ThreeSampleTests()
        inlist3=[4,7,-4,-5,6,8,-9.,2,-65,1,23,15,-7.5,6.,1,7,0.]
        inlist4=[1.2,-3,3,.1,2,56,754,35,-6,-44.,-7,-3,2,6.1,4.8,9.5,-7]
        Inlist3=M.array([inlist3,inlist3])
        Inlist4=M.array([inlist4,inlist4])
        if axis==0:
            Inlist3=M.transpose(Inlist3)
            Inlist4=M.transpose(Inlist4)

        print 'KruskalWallisH'
        TS.KruskalWallisH((inlist,inlist2,inlist3,inlist4))
        h,prob=genutil.salstat.KruskalWallisH(Inlist,Inlist2,Inlist3,Inlist4,axis=axis,df=0)
        if TS.h!=h[0] or TS.prob!=prob[0]:
            print 'Error KruskalWallisH !'
            print TS.h,h[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'KruskalWallisH ok'

        print 'FriedmanChiSquare'
        TS.FriedmanChiSquare((inlist,inlist2,inlist3,inlist4))
        sumranks,chisq,prob=genutil.salstat.FriedmanChiSquare(Inlist,Inlist2,Inlist3,Inlist4,axis=axis,df=0)
        if (not M.allequal(M.array(TS.sumranks),sumranks[:,0])) or TS.prob!=prob[0] or TS.chisq!=chisq[0]:
            print 'Error FriedmanChiSquare !'
            print TS.sumranks,sumranks[:,0]
            print TS.chisq,chisq[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'FriedmanChiSquare ok'

        print 'CochranesQ'
        TS.CochranesQ((inlist,inlist2,inlist3,inlist4))
        q,prob=genutil.salstat.CochranesQ(Inlist,Inlist2,Inlist3,Inlist4,axis=axis,df=0)
        if  TS.prob!=prob[0] or TS.q!=q[0]:
            print 'Error CochranesQ !'
            print TS.q,q[0]
            print TS.prob,prob[0]
            raise ''
        else:
            print 'CochranesQ ok'

        sums=[]
        means=[]
        ns=[]
        inlists=[inlist,inlist2,inlist3,inlist4]
        for l in inlists:
            ns.append(len(l))
            s=0
            for j in range(ns[-1]):
                s+=l[j]
            sums.append(s)
            means.append(s/float(ns[-1]))
        print 'anovaWithin'
        TS.anovaWithin(inlists,ns,sums,means)
        SSint, SSres, SSbet, SStot, MSbet, MSwit, MSres, F, prob  = genutil.salstat.anovaWithin(Inlist,Inlist2,Inlist3,Inlist4,axis=axis,df=0)
        attr=['SSint', 'SSres', 'SSbet', 'SStot', 'MSbet', 'MSwit', 'MSres', 'F', 'prob']
        ierr=0
        for a in attr:
            val=getattr(TS,a)
            exec('genval = '+a)
            if not M.allclose(val,genval[0]):
                ierr=1
                print 'error for ',a
        if ierr:
            print 'Error anovaWithin!'
            for b in attr:
                exec('v = '+b)
                print b,getattr(TS,b),v[0],getattr(TS,b)-v[0]
            raise ''
        else:
            print 'anovaWithin ok'

        print 'anovaBetween'
        desc=[]
        for i in inlists:
            desc.append(salstat_stats.FullDescriptives(i))
        TS.anovaBetween(desc)
        SSbet, SSwit, SStot, MSbet, MSerr, F, prob  = genutil.salstat.anovaBetween(Inlist,Inlist2,Inlist3,Inlist4,axis=axis,df=0)
        attr=['SSbet', 'SSwit', 'SStot', 'MSbet', 'MSerr', 'F', 'prob']
        ierr=0
        for a in attr:
            val=getattr(TS,a)
            exec('genval = '+a)
            if not M.allclose(val,genval[0]):
                ierr=1
                print 'error for ',a
        if ierr:
            print 'Error anovaBetween!'
            for b in attr:
                exec('v = '+b)
                print b,getattr(TS,b),v[0],getattr(TS,b)-v[0]
            raise ''
        else:
            print 'anovaBetween ok'

