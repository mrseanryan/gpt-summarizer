outdir=./temp/output

if [ -d "$outdir" ]; then
    rm -rf $outdir
fi

function test()
{
    mkdir -p $outdir
    poetry run python -m gpt-summarizer.main_cli ./data/input.txt  -o $outdir $1 $2 $3 $4

    ls -al $outdir
}

test

echo "== Run again - should skip files that already have an output =="

test
