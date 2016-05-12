
 var t=true;
var st=false;
var sx=window.innerWidth;
var left;
var cs=0;
var ele=[];
if(sx>960) left=300;
else if(sx>600)left =200;
else left=0;
$(document).ready(function(){
    //menu
     $(".bodym>ul>li>span").click(function(){
        $(this).toggleClass("minus");
        $(this).next().slideToggle("slow"); 
    });

    //Image
    
    $(".imghover>img").hover(function(){
  $(this).next().css("width",""+$(this).width()+"px");
    $(this).parent().css("width",""+$(this).width()+"px");
   
    $(this).parent().css("box-shadow","0 0 4px black");
    $(this).next().css("opacity","1");
   $(this).next().animate({fontSize:'18px'},'fast');
         
    }, function(){
    
   $(this).next().animate({fontSize:'0',opacity:'0'},'slow');
         $(this).parent().css("box-shadow","none");
    }); 
    
  
 


  //header-hover
    $(".header2").hover(function(){
    $(".logo2").addClass("rotate");
    $(".glare").css("visibility","visible").animate({left:'100%'},'slow');
},function(){
    if(st){ $(".searchb").animate({width:'0px'}).css("visibility","hidden");  st=false;}
    $(".logo2").removeClass("rotate");
    $(".glare").css("visibility","hidden").animate({left:'0px'},'fast');
}); 
    //search-bar
    $(".search").mouseenter(function(){
        st=true;
    $(".searchb").css("visibility","visible").animate({width:'200px'}).focus();
    });
   //menu
      $(".arrow").click(function(){
        if(t){
            if(left==0){
                 $(this).css({"-ms-transform":"rotate(180deg)","-webkit-transform":"rotate(180deg)","transform":"rotate(180deg)"});
                $('.bodyc').css('display','none');
            }
            else{
    $(this).css({"-ms-transform":"rotate(180deg)","-webkit-transform":"rotate(180deg)","transform":"rotate(180deg)"});
        $(".bodyc").animate({
            left: '+='+left+'px',
        width: '-='+left+'px'
        });
       } t=false;}
        else{
            if(left==0){
                $(this).css({"-ms-transform":"rotate(0deg)","-webkit-transform":"rotate(0deg)","transform":"rotate(0deg)"});
                $('.bodyc').css('display','block');
            }
            else{
    $(this).css({"-ms-transform":"rotate(0deg)","-webkit-transform":"rotate(0deg)","transform":"rotate(0deg)"});
        $(".bodyc").animate({
            left: '-='+left+'px',
        width: '+='+left+'px'
        });
        }
          t=true;   
        }
         
});
     //Log-in 
     $(".rightt").click(function(){
              if(t){
            if(left==0){
                 $('.arrow').css({"-ms-transform":"rotate(180deg)","-webkit-transform":"rotate(180deg)","transform":"rotate(180deg)"});
                $('.bodyc').css('display','none');
            }
            else{
    $('.arrow').css({"-ms-transform":"rotate(180deg)","-webkit-transform":"rotate(180deg)","transform":"rotate(180deg)"});
        $(".bodyc").animate({
            left: '+='+left+'px',
        width: '-='+left+'px'
        });
       } t=false;
 $(".bodym>form>fieldset>input[type='text']").focus();}
          });    
  
       

    //Regestration
    $('#rcpwd').keyup(function(){
   if($('#rcpwd').val()!=$('#rpwd').val()) {   
       $('.rmsg').text("Password do not match!").animate({opacity:'1'}); 
   }else{
        $('.rmsg').text("").animate({opacity:'0'}); 
   }
    });
     $('#rpwd').keyup(function(){
   if($('#rcpwd').val()!=$('#rpwd').val()) {   
       $('.rmsg').text("Password do not match!").animate({opacity:'1'}); 
   }else{
        $('.rmsg').text("").animate({opacity:'0'}); 
   }
    });
    
       var iiu=0;         
    $(".btn").click(function(){
        if(iiu==0)
        {$('.form:nth-child(1)').animate({marginLeft:'-110%'});
         $('.form:nth-child(2)').animate({marginLeft:'0px'});
         iiu=1;}
        else if(iiu==1){
             $('.form:nth-child(2)').animate({marginLeft:'-110%'});
         $('.form:nth-child(3)').animate({marginLeft:'110%'});
            iiu=2;
        }
    });
});
    
    //Slider
    
  /*  var sl=$(".slider");
   var n=$(".slider>img").length;
    
    
  ele[0]= $(".slider>img:nth-child(1)"); 
   ele[1]= $(".slider>img:nth-child(2)");
    ele[2]= $(".slider>img:nth-child(3)");

    
    var hei= ele[0].height();
  hei+=20;
  var wid=ele[0].width();
    
   sl.css({'height':''+hei+'px','overflow':'hidden'});
    var ho=true;
    var i=1;
    ele[1].css({'margin-top':'-'+hei+'px','margin-left':''+wid+20+'px'});
      ele[2].css({'margin-top':'-'+hei+'px','margin-left':''+wid+20+'px'});
   // ele[0].animate({'marginLeft':'-'+wid+10+'px'},3000);
     ele[1].delay(1000).animate({'marginLeft':'0px'},function(){ele[2].delay(1000).animate({'marginLeft':'0px'})});
slide(2000,n);    
 

     
    
});

function slide(d,n){
   if(cs==n-1){resets();}else{ele[cs].delay(2000).animate({'marginLeft':'0','marginTop':'0'},slide(++cs,d,n));}
}
function resets(){
    
    
}*/

/*
function slider(i,n,ho,hei){
  ele[1].animate({marginTop:'-'+hei+'px'},'slow');
     if(ho){
       if(i%n==0){
           
           var j;
         for(j=1;j<n;j++){
              ele[i%n].animate({marginTop:'0'},'slow');
              
          }
     }
          else {ele[i%n].animate({marginTop:'-'+hei+'px'},'slow');
                 }
       i++;
          }
});
*/