outdir=./temp/output
mkdir -p $outdir
python3 main_cli.py ./data/small_input  -o $outdir $1 $2 $3 $4

ls -al $outdir
