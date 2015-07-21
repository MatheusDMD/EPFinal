var PartyName = "";
var Password = "";

function voltar(e) {
	$.page2.close();
}

function ConfirmaDados(e) {
	if ($.txtusr.value === ""){
		alert("It is necessary to give the party name");
	}
	else {
		if ($.txtpwd.value !== $.txtconpwd.value){
			alert("The passwords are different");
		}
		else{
			PartyName = $.txtusr.value;
			Password = $.txtpwd.value;
			Alloy.Globals.credentials ={
       		PartyName : PartyName,
       		Password : Password
		    };
			var PartyPage = Alloy.createController("PartyPage").getView();
			PartyPage.open();
			$.page2.close();
			
			console.log(PartyName);
			console.log(Password);
		}
	}
}
