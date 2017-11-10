BEGIN{
    print "const unsigned short draw_" filename "[] PROGMEM = {"
}
/^G/{ split($0,coords,"[GXYZ]")
  if ( coords[2] == "00 " ) {
    laserOn=0 
  }
  if ( coords[2] == "01 " ) {
    laserOn=1
  }
  x=coords[3]
  y=coords[4]
  if ( x != "" && y != "") {
#    printf( "Before %s,%s,\n",x,y)
    x = (x + 20)
    y = (y - 18)
#    printf( "Offset %s,%s,\n",x,y)
    x = x * 20
    y = y * 20
#    printf( "Scaled %s,%s,\n",x,y)
    if ( laserOn == 1 ) {
      x = x + 32768
    }
#    printf( "Laser %s,%s,\n",x,y)
    printf( "0x%x,0x%x,\n",x,y)
  }
}
END{
    print "};"
}
