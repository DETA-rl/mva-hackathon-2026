BEGIN { FS = "\t" }
!/^#/ {
  n = split($8, a, ";")
  sig = ""; rs = ""; mc = ""; gene = ""; vc = ""
  for (i = 1; i <= n; i++) {
    if (a[i] ~ /^CLNSIG=/) sig = substr(a[i], 8)
    if (a[i] ~ /^CLNREVSTAT=/) rs = substr(a[i], 12)
    if (a[i] ~ /^MC=/) mc = substr(a[i], 4)
    if (a[i] ~ /^GENEINFO=/) { gene = substr(a[i], 10); sub(/:.*/, "", gene) }
    if (a[i] ~ /^CLNVC=/) vc = substr(a[i], 7)
  }
  if (vc != "single_nucleotide_variant") next
  if (gene == "BUB1B") next
  if (rs !~ /^(criteria_provided,_single_submitter|criteria_provided,_multiple_submitters,_no_conflicts|reviewed_by_expert_panel|practice_guideline)$/) next
  if (sig == "Pathogenic" || sig == "Likely_pathogenic") cls = "P"
  else if (sig == "Benign" || sig == "Likely_benign") cls = "B"
  else next
  if (mc ~ /stop_gained|nonsense/) t = "nonsense"
  else if (mc ~ /missense_variant/) t = "missense"
  else next
  cnt[cls " " t]++
  gcnt[cls " " t " " gene]++
}
END {
  for (k in cnt) print "COUNT", k, cnt[k]
  for (k in gcnt) print "GENE", k, gcnt[k]
}
