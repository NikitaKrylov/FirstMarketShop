function getInputQuantity(slug) {
    let InputString = document.querySelector('.product-value-input#'+slug)
    return InputString.value 
}


function minusValue(btn) {
    console.log('hello')
    let InputString = document.querySelector('.product-value-input#'+btn.id)
    let num = Number(InputString.value ) - 1
    if (num > 0) {
        InputString.value  =  num
    }
}



function plusValue(btn) {
    console.log('hello')
    let InputString = document.querySelector('.product-value-input#'+btn.id)
    let num = Number(InputString.value ) + 1
    if (num < 100) {
        InputString.value  =  num
    }
}


