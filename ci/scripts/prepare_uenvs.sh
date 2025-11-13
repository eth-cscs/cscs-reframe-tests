imgs=$(./ci/scripts/alps.sh uenv_image_find)
uenv repo status
for img in $imgs; do
    # Pull metadata from img
    echo "uenv_pull_meta_dir for $img!!"
	./ci/scripts/alps.sh uenv_pull_meta_dir "$img" &> .rc
	echo "meta_has_reframe_yaml"
	./ci/scripts/alps.sh meta_has_reframe_yaml "$img" &> .rc
	cat .rc
	rc=$(grep -q OK .rc ; echo $?)
	echo "rc=$rc"
	if [ $rc -eq 0 ] ; then
		UENVA+="$img,"
		echo "UENVA=$UENVA"
	fi
done
UENVA=${UENVA%?}
UENV=`echo ${UENVA} | sed 's-,,-,-g' | sort -u`
echo "UENV=$UENV" > rfm_uenv.env
cat rfm_uenv.env | tr , "\n"
