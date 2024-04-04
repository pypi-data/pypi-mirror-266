<?xml version="1.0" encoding="UTF-8" ?>
<request xmlns="http://www.isinet.com/xrpc42" src="app.id=API Demo">
  <fn name="LinksAMR.retrieve">
    <list>
      <!-- WHO'S REQUESTING -->
      <map>   
        <val name="username">{user}</val>       
        <val name="password">{password}</val>            
      </map>
      <!-- WHAT'S REQUESTED -->
      <map>
        <list name="WOS">
{{what}}
        </list>
      </map>
      <!-- LOOKUP DATA -->
      <map>
{{lookup}}
      </map>
    </list>
  </fn>
</request>
