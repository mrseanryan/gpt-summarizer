outdir=./temp/output

if [ -d "$outdir" ]; then
    rm -rf $outdir
fi

URL=https://raw.githubusercontent.com/mrseanryan/gpt-summarizer/master/README.md

function test_with_outdir()
{
    mkdir -p $outdir
    python3 main_cli.py $URL  -o $outdir $1 $2 $3 $4

    ls -al $outdir
}

test_with_outdir

echo "== Run again - should NOT skip files, since we download to new unique filepath =="

test_with_outdir

echo "== Run downloading a PDF file =="

URL=https://raw.githubusercontent.com/mrseanryan/gpt-summarizer/master/data/How-Language-Models-use-Long-Contexts.pdf

test_with_outdir
