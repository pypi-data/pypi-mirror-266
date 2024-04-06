RETCODE=0;
ls miaou.txt;
RETCODE=$RETCODE+$?;
ls ttt.sh;
RETCODE=$RETCODE+$?;
exit $(($RETCODE))
