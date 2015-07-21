function voltar(e){
	$.PartyPage.close();
}

function avancar(e){
	var buscar = Alloy.createController("buscar").getView();
	buscar.open();
}
