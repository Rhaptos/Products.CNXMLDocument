/*
  Javascript for simulating MathML on browsers that don't support it

  This is derived from David Carlisle's universal MathML stylesheet
  See http://www.w3.org/Math/XSL/
  
  Use and distribution of this code are permitted under the terms of the
  W3C Software Notice and License. See LICENSE.W3C for details.
*/

function malign (l)
{
    var m = 0;
    for ( i = 0; i < l.length ; i++)
	{
	    m = Math.max(m,l[i].offsetLeft);
	}
    for ( i = 0; i < l.length ; i++)
	{
	    l[i].style.marginLeft=m - l[i].offsetLeft;
	}
}

function mrowStretch (opid,opt,ope,opm,opb){
    opH = opid.offsetHeight;
    var opH;
    var i;
    var es;
    if (mrowH > opH * 2) {
	m= "<font size='+1' face='symbol'>" + opm + "</font><br/>" ;
	if ((mrowH < opH * 3) &&(opm == ope) ) m="";
	es="";
	for ( i = 3; i <= mrowH / (2*opH) ; i += 1) es += "<font size='+1' face='symbol'>" + ope + "</font><br/>" ;
	opid.innerHTML="<table class='lr'><tr><td><font size='+1' face='symbol'>" +
	    opt + "</font><br/>" +
	    es +
	    m +
	    es +
	    "<font size='+1' face='symbol'>" + opb + "</font></td></tr></table>";
    }
}

function msubsup (bs,bbs,x,b,p){
    //p.style.setExpression("top",bs +" .offsetTop - " + (p.offsetHeight/2 +(bbs.offsetHeight - Math.max(bbs.offsetHeight, b.offsetHeight + p.offsetHeight)*.5)));
    p.style.setExpression("top",bs +" .offsetTop -"  + (p.offsetHeight/2));
    b.style.setExpression("top",bs + ".offsetTop + " + (bbs.offsetHeight - b.offsetHeight*.5));
    x.style.setExpression("marginLeft",Math.max(p.offsetWidth,b.offsetWidth));
    document.recalc(true);
}

//function msubsupzz (bs,x,b,p){
//p.style.setExpression("top",bs +" .offsetTop - " + bs +
//"p.offsetHeight/2 +(" + bs + ".offsetHeight - Math.max(" + bs + ".offsetHeight, (" + bs + "b.offsetHeight + " + bs + "p.offsetHeight)*.5))");
//b.style.setExpression("top",bs + ".offsetTop + " + bs + ".offsetHeight -  " + bs + "b.offsetHeight/2");
//x.style.setExpression("marginLeft","Math.max(" + bs +"p.offsetWidth,"
//+ bs +"b.offsetWidth)");
//}

function msup (bs,x,p){
    p.style.setExpression("top",bs +" .offsetTop -"  + (p.offsetHeight/2));
    x.style.setExpression("marginLeft", bs +"p.offsetWidth");
    x.style.setExpression("height", bs + ".offsetHeight + " + p.offsetHeight);
    document.recalc(true);
}

function msub (bs,x,p){
    p.style.setExpression("top",bs +" .offsetTop +"  + (p.offsetHeight/2));
    x.style.setExpression("marginLeft", bs +"p.offsetWidth");
    x.style.setExpression("height", bs + ".offsetHeight + " + p.offsetHeight);
    document.recalc(true);
}

function toggle (x) {
    for ( i = 0 ; i < x.childNodes.length ; i++) {
	if (x.childNodes.item(i).style.display=='inline') {
	    x.childNodes.item(i).style.display='none';
	    if ( i+1 == x.childNodes.length) {
		x.childNodes.item(0).style.display='inline';
	    } else {
		x.childNodes.item(i+1).style.display='inline';
	    };
	    break;
	}
    }
}
