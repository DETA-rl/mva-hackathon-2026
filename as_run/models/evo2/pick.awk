BEGIN{FS="\t"}
($1=="11" && (($2==5227002 && $5=="A") || ($2==5226099) || ($2==5226197) || ($2==5226551) || ($2==5225911))) {
  n=split($8,a,";"); s="";
  for(i=1;i<=n;i++) if(a[i] ~ /^(CLNSIG|CLNDN|AF_TGP|GENEINFO|CLNREVSTAT)=/) s=s" "a[i];
  print $2,$3,$4,$5,s
}
