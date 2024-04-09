def vanillaMC_call(S,K, r,sig,T,sim):
    # S: 현재가
    # K: 행사가격
    # T: 만기(in years)
    # r: 이자율 (연 1%면 0.01로)
    # sig: 연변동성 (30%라면 0.3으로)

    import cupy as cp
    from scipy.stats import norm
    import matplotlib.pyplot as plt
    # 랜덤 시드 설정
    cp.random.seed(77)
    N_intervals=352 # 1년을 352로 세팅
    N = int(T * N_intervals)  # 만기를 감안한 시간간격의 갯수
    dt=T/N # 시간간격
    s = cp.sqrt(1 / N_intervals)  # 분산을 표준편차화

    # N(0,s)을 따르는 [N, sim] 크기의 정규난수 생성
    dW = cp.random.normal(0, s, size=(N, sim))
    pars=(r-0.5*sig*sig)*dt+sig*dW
    exp_pars=cp.exp(pars)

    # 추가할 행 생성
    S0 = S*cp.ones((1, dW.shape[1]), dtype=dW.dtype)
    W = cp.vstack([S0, exp_pars]) # (N+1,sim)의 행렬로 만든다.

    # 시간에 따른 주가행렬 완성
    S=cp.cumprod(W,axis=0) # 행으로 계속 누적곱셈으로 행렬 생성

    # 옵션 payoff
    option=cp.maximum(S[-1]-K,0) # 콜옵션
    price=cp.mean(cp.exp(-r*T)*option)
    return price

def vanillaMC_call_Greeks(S,K, r,sig,T,sim):
    dp=S*0.01
    P0=vanillaMC_call(S,K, r,sig,T,sim)
    Pup=vanillaMC_call(S+dp,K, r,sig,T,sim)
    Pdn=vanillaMC_call(S-dp,K, r,sig,T,sim)
    delta= (Pup-Pdn)/(2*dp)
    gamma=(Pup-2*P0+Pdn)/(dp*dp)
    Pv=vanillaMC_call(S,K, r,sig+0.01,T,sim)
    vega=Pv-P0
    Pr=vanillaMC_call(S,K, r+0.0001,sig,T,sim)
    rho=Pr-P0
    Pt=vanillaMC_call(S,K, r,sig,T-1/365,sim)
    theta=Pt-P0
    print('델타:',delta)
    print('감마:',gamma)
    print('1% 베가:',vega)
    print('1bp 르호:',rho)
    print('1Day 세타:',theta)
