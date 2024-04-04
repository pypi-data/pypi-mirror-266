FILENAME='tmpname_output_pmgetter'
QUERY='breast cancer[MESH] has abstract[FILT] journal article[PTYP] english[LANG] 1990:2014[PDAT]'

cat $0 > $FILENAME'.src' \
&&
echo -e '<?xml version="1.0" ?>\n<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2017//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_170101.dtd">\n<xml>' > $FILENAME'.xml' \
&&
~/edirect/esearch -db pubmed -query "$QUERY"  \
|
~/edirect/efetch -format xml \
|
grep -vE '<\?xml version="1.0" \?>|<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle' >> $FILENAME'.xml' \
&&
echo '</xml>' >> $FILENAME'.xml'

