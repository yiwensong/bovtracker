import re
import sys
import getopt

"""This function is supposed to just read your hands and your chip counts for a single
tournament. We might expand this to include more shit later."""

# REGEX FORMATTING FOR VARIOUS THINGS THAT I WANT TO DO
RE_GET_CHIP_COUNT         = r'.*\[ME\] \((.*) in chips\)'
RE_GET_BLINDS             = r'.*Bovada Hand #.*:.* \((.*)/(.*)\).*'
RE_GET_VPIP_COUNT_PRE     = r'\** HOLE CARDS \**'
RE_GET_VPIP_COUNT_CALL    = r'.*\[ME\].*Call.*'
RE_GET_VPIP_COUNT_RAISE   = r'.*\[ME\].*Raises.*'
RE_GET_VPIP_COUNT_FOLD    = r'.*\[ME\].*Folds.*'

# REGEX COMPILE
RE_COMPILED_BLINDS            = re.compile(RE_GET_BLINDS)
RE_COMPILED_CHIP_COUNTER      = re.compile(RE_GET_CHIP_COUNT)
RE_COMPILED_VPIP_COUNT_CALL   = re.compile(RE_GET_VPIP_COUNT_CALL )
RE_COMPILED_VPIP_COUNT_RAISE  = re.compile(RE_GET_VPIP_COUNT_RAISE)
RE_COMPILED_VPIP_COUNT_FOLD   = re.compile(RE_GET_VPIP_COUNT_FOLD )


def analyze(fd,wrfd):
  """This will attempt to plot the chip count change in a single tournament. May or may not work
since my X server is not working, I don't think."""

  vpip_total = 0
  vpip_flag = 0
  handno = 0

  wrfd.write("hand no,stack count (chips),stack count (BB),small blind,big blind\n")

  while True:
    buf = fd.readline()
    if buf=="":
      break
    #ENDIF
    blinds = RE_COMPILED_BLINDS.match(buf)
    if not blinds == None:
      blindlevel = [int(blinds.group(1)),int(blinds.group(2))]
    #ENDIF
    match = RE_COMPILED_CHIP_COUNTER.match(buf)
    if not match == None:
      match = re.split(',',match.group(1))
      matchnum = 0
      for num in match:
        matchnum *= 1000
        matchnum += int(num)
      #ENDFOR
      match = matchnum
      handno += 1
      wrstr = "{},{},{},{},{}\n".format(handno,match,int(float(match)/float(blindlevel[1])),blindlevel[0],blindlevel[1])
      wrfd.write(wrstr)
    #ENDIF
    preflop = re.match(RE_GET_VPIP_COUNT_PRE,buf)
    if not preflop == None:
      vpip_flag = 1
    #ENDIF
    if vpip_flag:
      call = RE_COMPILED_VPIP_COUNT_CALL.match(buf)
      rais = RE_COMPILED_VPIP_COUNT_RAISE.match(buf)
      fold = RE_COMPILED_VPIP_COUNT_FOLD.match(buf)
      if not call == None or not rais == None or not fold == None:
        vpip_flag = 0
      #ENDIF
      if not call == None or not rais == None:
        vpip_total += 1
      #ENDIF
    #ENDIF
  #ENDWHILE

  vpip = float(vpip_total)/float(handno)
  vpipstr = "vpip,{}".format(vpip)
  wrfd.write(vpipstr)

  return 0
#ENDDEF

def main():
  """USAGE: test_read.py input_file_name [output_file_name]"""
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hd",["help","doc"])
  except getopt.error, msg:
    print msg
    print "for help use --help"
    sys.exit(2)
  #ENDTRY

  for o,a in opts:
    if o in ("-h","--help"):
      print main.__doc__
    elif o in ("--doc","-d"):
      print analyze.__doc__
    #ENDIF
    sys.exit(0)
  #ENDFOR

  if len(args) < 1:
    print >>sys.stderr,"test_read.py error: not enough arguments\nfor help use --help"
    sys.exit(2)
  #ENDIF

  if len(args) > 2:
    print "test_read.py warning: unused arguments"
  #ENDIF

  exit_flag = False

  try:
    fd = open(args[0],'r')
  except IOError:
    print >>sys.stderr,"test_read.py error: file not found", args[0]
    exit_flag = True
  #ENDTRY

  if len(args) == 2:
    try:
      wrfd = open(args[1],'w')
    except IOError:
      print >>sys.stderr, "test_read.py error: file cannot be opened for writing", args[1]
      exit_flag = True
    #ENDTRY
  else:
    wrfd = open('DEFAULT_OUTPUT.csv','w')
  #ENDIF


  if exit_flag:
    print >>sys.stderr,"file could not be loaded\ntest_read.py exiting"
    sys.exit(0)
  #ENDIF

  check_flag = analyze(fd,wrfd)
  
  fd.close()
  wrfd.close()

  if check_flag:
    print >>sys.stderr,"something went wrong\n\
      try 'python test_read.py -d' to see implementation details"
  #ENDIF
#ENDDEF

if __name__ == "__main__":
  main()
#ENDIF
