cd `dirname $0`
BIN_DIR=`pwd`
cd ..
DEPLOY_DIR=`pwd`
MAIN_CLASS=com.ctfo.sjyypt.hbaseservice.manager2.JMXClient
LIB_DIR=$DEPLOY_DIR/lib
LIB_JARS=`ls $LIB_DIR|grep .jar|awk '{print "'$LIB_DIR'/"$0}'|tr "\n" ":"`
java -cp $LIB_JARS $MAIN_CLASS 1099 $1
