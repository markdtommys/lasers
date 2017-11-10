BEGIN{
    print "const unsigned short draw_" filename "[] PROGMEM = {"
}
/^G00/{ laserOn=0 }
/^G01/{ laserOn=1 }
/^X/{
  split($0,coords,"[XY]")
  x=coords[2]
  x = x * 100
  y=coords[3]
  y = y * 100
  if ( laserOn == 1 ) {
    x = x + 32768
  }
  printf( "0x%x,0x%x,\n",x,y)
}
END{
    print "};"
}
