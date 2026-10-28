from itertools import permutations
def d(n):
    c=0;i=1
    while i*i<=n:
        if n%i==0: c+= 1 if i*i==n else 2
        i+=1
    return c
print('S1', sum(1 for n in range(1,10001) if d(n)==4 and d(n+1)==4))
print('S2', sum(1 for p in permutations(range(1,9)) if all(p[i]!=i+1 for i in range(8)) and all(abs(p[i]-p[i+1])!=1 for i in range(7))))
pr=lambda n: n>1 and all(n%k for k in range(2,int(n**.5)+1))
print('S3', sum(p for p in range(1000) if pr(p) and pr(p+2) and pr(p+6)))
