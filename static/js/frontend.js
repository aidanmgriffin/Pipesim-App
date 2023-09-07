function CheckAll() {
    
    var checkBox = document.getElementById("flexCheckDefault");
    var checkBoxStagnant = document.getElementById("flexCheckStagnant");
    var checkBoxAdvective = document.getElementById("flexCheckAdvective");
    var labelStagnant = document.getElementById("stagnant-periods");
    var labelAdvective = document.getElementById("advective-periods");

    var text = document.getElementById("text");

    if (checkBox.checked == true){
        checkBoxAdvective.style.display = "block"
        checkBoxStagnant.style.display = "block"
        labelAdvective.style.display = "block"
        labelStagnant.style.display = "block"
        checkBoxStagnant.checked = true
        checkBoxAdvective.checked = true
    }
    else {
        checkBoxAdvective.style.display = "none"
        checkBoxStagnant.style.display = "none"
        labelAdvective.style.display = "none"
        labelStagnant.style.display = "none"
        checkBoxStagnant.checked = false
        checkBoxAdvective.checked = false
    }

    if (checkBoxAdvective.checked == false && checkBoxStagnant.checked == false && checkBox.checked == true){
        checkBox.checked = false
        checkBoxAdvective.style.display = "none"
        checkBoxStagnant.style.display = "none"
        labelAdvective.style.display = "none"
        labelStagnant.style.display = "none"
    }
}

function UncheckAll() {

    var checkBox = document.getElementById("flexCheckDefault");
    var checkBoxStagnant = document.getElementById("flexCheckStagnant");
    var checkBoxAdvective = document.getElementById("flexCheckAdvective");
    var labelStagnant = document.getElementById("stagnant-periods");
    var labelAdvective = document.getElementById("advective-periods");

   

    if (checkBoxAdvective.checked == false && checkBoxStagnant.checked == false && checkBox.checked == true){
        checkBox.checked = false
        checkBoxAdvective.style.display = "none"
        checkBoxStagnant.style.display = "none"
        labelAdvective.style.display = "none"
        labelStagnant.style.display = "none"
    }
}