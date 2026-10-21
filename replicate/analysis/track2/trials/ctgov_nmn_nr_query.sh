curl -s --max-time 90 "https://clinicaltrials.gov/api/v2/studies?query.term=nicotinamide+mononucleotide+OR+NMN+OR+nicotinamide+riboside&filter.overallStatus=RECRUITING,ACTIVE_NOT_RECRUITING,COMPLETED,NOT_YET_RECRUITING&pageSize=200&fields=NCTId,BriefTitle,OverallStatus,Phase,Condition,EnrollmentCount" | python3 -c "
import sys,json
d=json.load(sys.stdin); st=d.get('studies',[])
print('total studies:',len(st))
kw=('muscle','sarcopen','kidney','renal','nephro','atrophy','cachexia','frail')
for s in st:
  p=s['protocolSection']; i=p['identificationModule']; c=p.get('conditionsModule',{}).get('conditions',[]); ds=p.get('statusModule',{}).get('overallStatus')
  t=i.get('briefTitle','')
  flag='*' if any(k in (t+' '.join(c)).lower() for k in kw) else ' '
  print(flag,i['nctId'],ds,'|',t[:90],'|',', '.join(c)[:60])
" ; echo "--- wait: ClinicalTrials.gov count with muscle/kidney"
