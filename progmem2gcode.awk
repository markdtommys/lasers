{
  split($0,coords,",")
  x=strtonum(coords[1])
  y=strtonum(coords[2])
  if ( x > 32768 ) {
    x = x - 32768
    d = 1
  } else {
    d = 0
  }
  print "D=" d " X=" x " Y=" y
}
