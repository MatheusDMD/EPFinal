var args = arguments[0] || {};

function voltar(e){
	$.buscar.close();
}

function avancar(e){
	var buscarfesta = Alloy.createController("buscarfesta").getView();
	buscarfesta.open();
}
