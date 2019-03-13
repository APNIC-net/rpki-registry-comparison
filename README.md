# how to detect alignment of RPKI certificates and registry (sub)accounts

## Summary: the pipeline in one go

```
# for some certificate e.g. ./Y1vTOT_M9475iEK4qDNIlUnlneM.cer
./readwhichopenssl.py ./Y1vTOT_M9475iEK4qDNIlUnlneM.cer | \
./delegfilter.py -s, -t cc,orgid -n 3 | \
cut -d, -f6 | sort | uniq -c | sort -nr 
```

## Dependencies

this code is for python3 and depends on the py-radix module

```pip3 install py-radix```

## Process

 1. fetch the repository

```rsync --delete -az rpki.cnnic.cn::rpki cnnic/```

 2. extract list of resources per certificate

by hand:

``` $ openssl x509 \
        -inform DER \
        -noout \
        -text \
        -in ./Y1vTOT_M9475iEK4qDNIlUnlneM.cer
```

scripted:

```./readwhichopenssl.py ./Y1vTOT_M9475iEK4qDNIlUnlneM.cer \
        > ./Y1vTOT_M9475iEK4qDNIlUnlneM.inr.txt
```
This generates data of the form:
```
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d480::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d580::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d680::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d780::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d880::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:d980::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:da80::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:db80::/32
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:dc80::/32
```

 3. filter the prefixes by RIR delegated file to tag by opaque-id field

the python program uses 0.. index fields so the field is 3, not 4.

```
    ./delegfilter.py -s, -t cc,orgid -n 3 \
        < Y1vTOT_M9475iEK4qDNIlUnlneM.inr.txt \
        > Y1vTOT_M9475iEK4qDNIlUnlneM.inr.orgid.txt
```

This generates data of the form:
```
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:f680::/32,CN,A9296B6E
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:f780::/32,CN,A92AE313
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:f880::/32,CN,A9246823
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:f980::/32,CN,A92D59A7
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:fa80::/32,CN,A92690D9
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:fb80::/32,CN,A92F4C61
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:fc80::/32,CN,A92F4D2B
./Y1vTOT_M9475iEK4qDNIlUnlneM.cer,635BD3393FCCF78EF98842B8A833489549E59DE3,IPv6,2407:fd80::/32,CN,A926F87F
```

 4. collate by opaque-id, count..

cut uses 1.. index fields so the field on output is 6 not 5 

```
    cut -d, -f6 < Y1vTOT_M9475iEK4qDNIlUnlneM.inr.orgid.txt | \
        sort | \
        uniq -c |\
        sort -nr \
        > Y1vTOT_M9475iEK4qDNIlUnlneM.orgid.counts.txt
```
