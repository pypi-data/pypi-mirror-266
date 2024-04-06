% diagram_0_massless_triangle_0.mp -- do not edit, generated automatically by 0_massless_triangle_0.tex
input feynmp
require_RCS_revision "1.30";
 style_def my_phantom_arrow expr p = draw_phantom_arrow p; shrink (1.50); cfill (arrow p); endshrink; enddef; 
 style_def my_double_phantom_arrow expr p = draw_phantom_arrow p; shrink (2.00); cfill (arrow p); endshrink; enddef; 
beginchar(1, 1500*1.0pt#, 1200*1.0pt#, 0);
"feynmf: 1";
LaTeX_unitlength:=1.0pt;
subgraph (0, 0, w, h);
vinit;
pickup pencircle scaled thin;
vleft (__v0);
vright (__v1, __v2);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=p1$|\phi 0|p_{1}$,label.dist=13.00", __v0, __v3);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v0, __v3);
vconnect ("phantom,width=1.75,fore=black,tension=3.00,label.dist=13.00", __v0, __v3);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=p2$|\phi 0|p_{2}$,label.dist=13.00", __v4, __v1);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v4, __v1);
vconnect ("phantom,width=1.75,fore=black,tension=3.00,label.dist=13.00", __v4, __v1);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=p3$|\phi 0|p_{3}|(p_{1}-p_{2})$,label.dist=13.00", __v5, __v2);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v5, __v2);
vconnect ("phantom,width=1.75,fore=black,tension=3.00,label.dist=13.00", __v5, __v2);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=q1$|\phi 0|(k_{0}+p_{2})$,label.dist=13.00", __v3, __v4);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v3, __v4);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=q2$|\phi 0|k_{0}$,label.dist=13.00", __v4, __v5);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v4, __v5);
vconnect ("my_phantom_arrow,width=1.75,fore=red,tension=0,label.dist=13.00", __v4, __v5);
vconnect ("dashes,width=1.75,fore=black,tension=1.00,label=q3$|\phi 0|(k_{0}-p_{1}+p_{2})$,label.dist=13.00", __v5, __v3);
vconnect ("my_phantom_arrow,width=1.75,fore=blue,tension=0,label.dist=13.00", __v5, __v3);
vlabel ("v4", __v3);
vvertex ("decor.shape=circle,decor.filled=full,label.dist=13.00,decor.size=5.00thick", __v3);
vlabel ("v5", __v4);
vvertex ("decor.shape=circle,decor.filled=full,label.dist=13.00,decor.size=5.00thick", __v4);
vlabel ("v6", __v5);
vvertex ("decor.shape=circle,decor.filled=full,label.dist=13.00,decor.size=5.00thick", __v5);
vfreeze;
vdraw;
endsubgraph;
endchar;
% the end.
end.
endinput;
