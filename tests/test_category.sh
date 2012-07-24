#!/bin/sh

ERROUTPUT=`mktemp`
TESTOUTPUT=`mktemp`

cleanup()
{
    rm -f $ERROUTPUT 2> /dev/null
    rm -f $TESTOUTPUT 2> /dev/null
    return 0
}

fatal()
{
    echo '***' "$@" >&2
    cleanup
    exit 1
}

CATEGORY=$1
ROOTDIR=$2
TESTS=`ls $CATEGORY/*/command 2> /dev/null | sed 's|/command||; s|.*/||' | sort`

if [ -z "$CATEGORY" ] ; then
    fatal No test directory specified.
fi
if [ -z "$ROOTDIR" -o ! -d "$ROOTDIR" ] ; then
    fatal No valid test root directory specified.
fi

echo Running tests for $CATEGORY
for TEST in $TESTS ; do
    echo "    $TEST"
    export TESTDIR=`pwd`/$CATEGORY/$TEST

    if [ -f $TESTDIR/input -a -f $TESTDIR/output ] ; then
        ( cd $ROOTDIR && sh $TESTDIR/command ) \
            < $TESTDIR/input 2> $ERROUTPUT > $TESTOUTPUT
        EXITSTATUS=$?
    elif [ -f $TESTDIR/input ] ; then
        ( cd $ROOTDIR && sh $TESTDIR/command ) \
            < $TESTDIR/input 2> $ERROUTPUT > /dev/null
        EXITSTATUS=$?
    elif [ -f $TESTDIR/output ] ; then
        ( cd $ROOTDIR && sh $TESTDIR/command ) 2> $ERROUTPUT > $TESTOUTPUT
        EXITSTATUS=$?
    elif [ -f $TESTDIR/status ] ; then
        ( cd $ROOTDIR && sh $TESTDIR/command ) 2> $ERROUTPUT > /dev/null
        EXITSTATUS=$?
    fi

    if [ ! -f $TESTDIR/status -a ! -f $TESTDIR/output ] ; then
        fatal "Bad test case; no expected output or exit status provided."
    fi

    if [ -f $TESTDIR/status ] ; then
        EXPECTED_STATUS=`cat $TESTDIR/status`
        if [ "$EXITSTATUS" != "$EXPECTED_STATUS" ] ; then
            cat $ERROUTPUT >&2
            fatal "Bad exit status; expected $EXPECTED_STATUS, got $EXITSTATUS."
        fi
    fi

    if [ -f $TESTDIR/output ] ; then
        if ! cmp -s $TESTDIR/output $TESTOUTPUT ; then
            diff -u $TESTDIR/output $TESTOUTPUT | \
                sed -e '1s/--- [^ ][^ ]*/--- expected-output/' \
                    -e '2s/+++ [^ ][^ ]*/+++ actual-output/'
            fatal "Unexpected command output (see diff above)."
        fi
    fi
done
cleanup
