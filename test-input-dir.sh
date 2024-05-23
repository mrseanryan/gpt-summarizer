outdir=./temp/output

if [ -d "$outdir" ]; then
    rm -rf $outdir
fi

function test_with_outdir()
{
    mkdir -p $outdir
    python3 main_cli.py ./data/small_input  -o $outdir $1 $2 $3 $4

    ls -al $outdir
}

test_with_outdir

echo "== Run again - should skip files that already have an output =="

test_with_outdir
