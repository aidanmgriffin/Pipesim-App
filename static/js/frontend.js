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

function monochloramineNetworkCheckAll() {

    var checkBox = document.getElementById("flexCheckMonochloramineNetworkDecay");
    var checkBoxHypochlorousAcid = document.getElementById("flexCheckHypochlorousAcidDecay");
    var checkBoxAmmonia = document.getElementById("flexCheckAmmoniaDecay");
    var checkBoxMonochloramine = document.getElementById("flexCheckMonochloramineDecay");
    var checkBoxDichloramine = document.getElementById("flexCheckDichloramineDecay");
    var checkBoxIodine = document.getElementById("flexCheckIodineDecay");
    var checkBoxDOCb = document.getElementById("flexCheckDOCbDecay");
    var checkBoxDOCbox = document.getElementById("flexCheckDOCboxDecay");
    var checkBoxDOCw = document.getElementById("flexCheckDOCwDecay");
    var checkBoxDOCwox = document.getElementById("flexCheckDOCwoxDecay");
    var checkBoxChlorine = document.getElementById("flexCheckChlorineDecay");

    var label = document.getElementById("monochloramine-network-decay");
    var labelHypochlorousAcid = document.getElementById("hypochlorous-acid-decay");
    var labelAmmonia = document.getElementById("ammonia-decay");
    var labelMonochloramine = document.getElementById("monochloramine-decay");
    var labelDichloramine = document.getElementById("dichloramine-decay");
    var labelIodine = document.getElementById("iodine-decay");
    var labelDOCb = document.getElementById("docb-decay");
    var labelDOCbox = document.getElementById("docbox-decay");
    var labelDOCw = document.getElementById("docw-decay");
    var labelDOCwox = document.getElementById("docwox-decay");
    var labelChlorine = document.getElementById("chlorine-decay");

    var inputHypochlorous = document.getElementById("label-hypochlorous");
    var inputAmmonia = document.getElementById("label-ammonia");
    var inputMonochloramine = document.getElementById("label-monochloramine");
    var inputDichloramine = document.getElementById("label-dichloramine");
    var inputIodine = document.getElementById("label-iodine");
    var inputDOCb = document.getElementById("label-docb");
    var inputDOCbox = document.getElementById("label-docbox");
    var inputDOCw = document.getElementById("label-docw")
    var inputDOCwox = document.getElementById("label-docwox")
    var inputChlorine = document.getElementById("label-chlorine")



    if (checkBox.checked == true){
        // checkBox.checked = true
        checkBoxHypochlorousAcid.style.display = "block"
        checkBoxAmmonia.style.display = "block"
        checkBoxMonochloramine.style.display = "block"
        checkBoxDichloramine.style.display = "block"
        checkBoxIodine.style.display = "block"
        checkBoxDOCb.style.display = "block"
        checkBoxDOCbox.style.display = "block"
        checkBoxDOCw.style.display = "block"
        checkBoxDOCwox.style.display = "block"
        checkBoxChlorine.style.display = "block"
        labelHypochlorousAcid.style.display = "block"
        labelAmmonia.style.display = "block"
        labelMonochloramine.style.display = "block"
        labelDichloramine.style.display = "block"
        labelIodine.style.display = "block"
        labelDOCb.style.display = "block"
        labelDOCbox.style.display = "block"
        labelDOCw.style.display = "block"
        labelDOCwox.style.display = "block"
        labelChlorine.style.display = "block"
        checkBoxHypochlorousAcid.checked = true
        checkBoxAmmonia.checked = true
        checkBoxMonochloramine.checked = true
        checkBoxDichloramine.checked = true
        checkBoxIodine.checked = true
        checkBoxDOCb.checked = true
        checkBoxDOCbox.checked = true
        checkBoxDOCw.checked = true
        checkBoxDOCwox.checked = true
        checkBoxChlorine.checked = true
        inputHypochlorous.style.display = "block"
        inputAmmonia.style.display = "block"
        inputMonochloramine.style.display = "block"
        inputDichloramine.style.display = "block"
        inputIodine.style.display = "block"
        inputDOCb.style.display = "block"
        inputDOCbox.style.display = "block"
        inputDOCw.style.display = "block"
        inputDOCwox.style.display = "block"
        inputChlorine.style.display = "block"

    }
    else {
        checkBoxHypochlorousAcid.style.display = "none"
        checkBoxAmmonia.style.display = "none"
        checkBoxMonochloramine.style.display = "none"
        checkBoxDichloramine.style.display = "none"
        checkBoxIodine.style.display = "none"
        checkBoxDOCb.style.display = "none"
        checkBoxDOCbox.style.display = "none"
        checkBoxDOCw.style.display = "none"
        checkBoxDOCwox.style.display = "none"
        checkBoxChlorine.style.display = "none"
        labelHypochlorousAcid.style.display = "none"
        labelAmmonia.style.display = "none"
        labelMonochloramine.style.display = "none"
        labelDichloramine.style.display = "none"
        labelIodine.style.display = "none"
        labelDOCb.style.display = "none"
        labelDOCbox.style.display = "none"
        labelDOCw.style.display = "none"
        labelDOCwox.style.display = "none"
        labelChlorine.style.display = "none"
        checkBoxHypochlorousAcid.checked = false
        checkBoxAmmonia.checked = false
        checkBoxMonochloramine.checked = false
        checkBoxDichloramine.checked = false
        checkBoxIodine.checked = false
        checkBoxDOCb.checked = false
        checkBoxDOCbox.checked = false
        checkBoxDOCw.checked = false
        checkBoxDOCwox.checked = false
        checkBoxChlorine.checked = false
        inputHypochlorous.style.display = "none"
        inputAmmonia.style.display = "none"
        inputMonochloramine.style.display = "none"
        inputDichloramine.style.display = "none"
        inputIodine.style.display = "none"
        inputDOCb.style.display = "none"
        inputDOCbox.style.display = "none"
        inputDOCw.style.display = "none"
        inputDOCwox.style.display = "none"
        inputChlorine.style.display = "none"
    }

    if ( 
        checkBoxHypochlorousAcid.checked == false && 
        checkBoxAmmonia.checked == false  &&
        checkBoxMonochloramine.checked == false &&
        checkBoxDichloramine.checked == false &&
        checkBoxIodine.checked == false &&
        checkBoxDOCb.checked == false &&
        checkBoxDOCbox.checked == false &&
        checkBoxDOCw.checked == false &&
        checkBoxDOCwox.checked == false &&
        checkBoxChlorine.checked == false &&
        checkBox.checked == true) 
        {
        checkBox.checked = false
        checkBoxHypochlorousAcid.style.display = "none"
        checkBoxAmmonia.style.display = "none"
        checkBoxMonochloramine.style.display = "none"
        checkBoxDichloramine.style.display = "none"
        checkBoxIodine.style.display = "none"
        checkBoxDOCb.style.display = "none"
        checkBoxDOCbox.style.display = "none"
        checkBoxDOCw.style.display = "none"
        checkBoxDOCwox.style.display = "none"
        checkBoxChlorine.style.display = "none"
        }

    // if (checkBoxAdvective.checked == false && checkBoxStagnant.checked == false && checkBox.checked == true){
    //     checkBox.checked = false
    //     checkBoxAdvective.style.display = "none"
    //     checkBoxStagnant.style.display = "none"
    //     labelAdvective.style.display = "none"
    //     labelStagnant.style.display = "none"
    // }

}

function monochloramineUncheckAll() {
    var checkBox = document.getElementById("flexCheckMonochloramineNetworkDecay");
    var checkBoxHypochlorousAcid = document.getElementById("flexCheckHypochlorousAcidDecay");
    var checkBoxAmmonia = document.getElementById("flexCheckAmmoniaDecay");
    var checkBoxMonochloramine = document.getElementById("flexCheckMonochloramineDecay");
    var checkBoxDichloramine = document.getElementById("flexCheckDichloramineDecay");
    var checkBoxIodine = document.getElementById("flexCheckIodineDecay");
    var checkBoxDOCb = document.getElementById("flexCheckDOCbDecay");
    var checkBoxDOCbox = document.getElementById("flexCheckDOCboxDecay");
    var checkBoxDOCw = document.getElementById("flexCheckDOCwDecay");
    var checkBoxDOCwox = document.getElementById("flexCheckDOCwoxDecay");
    var checkBoxChlorine = document.getElementById("flexCheckChlorineDecay");
    var labelHypochlorousAcid = document.getElementById("hypochlorous-acid-decay");
    var labelAmmonia = document.getElementById("ammonia-decay");
    var labelMonochloramine = document.getElementById("monochloramine-decay");
    var labelDichloramine = document.getElementById("dichloramine-decay");
    var labelIodine = document.getElementById("iodine-decay");
    var labelDOCb = document.getElementById("docb-decay");
    var labelDOCbox = document.getElementById("docbox-decay");
    var labelDOCw = document.getElementById("docw-decay");
    var labelDOCwox = document.getElementById("docwox-decay");
    var labelChlorine = document.getElementById("chlorine-decay");
    
    if( 
        checkBoxHypochlorousAcid.checked == false &&
        checkBoxAmmonia.checked == false &&
        checkBoxMonochloramine.checked == false &&
        checkBoxDichloramine.checked == false &&
        checkBoxIodine.checked == false &&
        checkBoxDOCb.checked == false &&
        checkBoxDOCbox.checked == false &&
        checkBoxDOCw.checked == false &&
        checkBoxDOCwox.checked == false &&
        checkBoxChlorine.checked == false &&
        checkBox.checked == true 
        ) {
        checkBox.checked = false
        checkBoxHypochlorousAcid.style.display = "none"
        checkBoxAmmonia.style.display = "none"
        checkBoxMonochloramine.style.display = "none"
        checkBoxDichloramine.style.display = "none"
        checkBoxIodine.style.display = "none"
        checkBoxDOCb.style.display = "none"
        checkBoxDOCbox.style.display = "none"
        checkBoxDOCw.style.display = "none"
        checkBoxDOCwox.style.display = "none"
        checkBoxChlorine.style.display = "none"
        labelHypochlorousAcid.style.display = "none"
        labelAmmonia.style.display = "none"
        labelMonochloramine.style.display = "none"
        labelDichloramine.style.display = "none"
        labelIodine.style.display = "none"
        labelDOCb.style.display = "none"
        labelDOCbox.style.display = "none"
        labelDOCw.style.display = "none"
        labelDOCwox.style.display = "none"
        labelChlorine.style.display = "none"

        }
    }

function concentrationCheckAll () {
    var checkBox = document.getElementById("flexCheckFreeChlorineDecay");
    var label1 = document.getElementById("label-1");
    var label2 = document.getElementById("label-2");
    var label3 = document.getElementById("label-3");
    var label4 = document.getElementById("label-4");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration");

    var text = document.getElementById("text");

    if (checkBox.checked == true){
        label1.style.display = "block"
        label2.style.display = "block"
        label3.style.display = "block"
        label4.style.display = "block"
        startingParticles.required = true
        injectedParticles.required = true

    }
    else {
        label1.style.display = "none"
        label2.style.display = "none"
        label3.style.display = "none"
        label4.style.display = "none"
        startingParticles.required = false
        injectedParticles.required = false
        
    }
}

function hypochlorousCheckAll () {
    var checkBox = document.getElementById("flexCheckHypochlorousAcidDecay");
    var label = document.getElementById("label-hypochlorous");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-hypochlorous");
    var injectedParticles= document.getElementById("injected-particles-free-chlorine-concentration-hypochlorous");

    var text = document.getElementById("text");

    if (checkBox.checked == true){
        label.style.display = "block"
        startingParticles.required = true
        injectedParticles.required = true
    }
    else {
        label.style.display = "none"
        startingParticles.required = false
        injectedParticles.required = false
    }
}

function ammoniaCheckAll() {
    var checkBox = document.getElementById("flexCheckAmmoniaDecay");
    var label = document.getElementById("label-ammonia");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-ammonia");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-ammonia");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function monochloramineCheckAll() {
    var checkBox = document.getElementById("flexCheckMonochloramineDecay");
    var label = document.getElementById("label-monochloramine");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-monochloramine");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-monochloramine");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function dichloramineCheckAll() {
    var checkBox = document.getElementById("flexCheckDichloramineDecay");
    var label = document.getElementById("label-dichloramine");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-dichloramine");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-dichloramine");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function iodineCheckAll() {
    var checkBox = document.getElementById("flexCheckIodineDecay");
    var label = document.getElementById("label-iodine");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-iodine");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-iodine");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function docbCheckAll() {
    var checkBox = document.getElementById("flexCheckDOCbDecay");
    var label = document.getElementById("label-docb");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-docb");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-docb");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function docboxCheckAll() {
    var checkBox = document.getElementById("flexCheckDOCboxDecay");
    var label = document.getElementById("label-docbox");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-docbox");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-docbox");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function docwCheckAll() {
    var checkBox = document.getElementById("flexCheckDOCwDecay");
    var label = document.getElementById("label-docw");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-docw");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-docw");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function docwoxCheckAll() {
    var checkBox = document.getElementById("flexCheckDOCwoxDecay");
    var label = document.getElementById("label-docwox");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-docwox");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-docwox");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function chlorineCheckAll() {
    var checkBox = document.getElementById("flexCheckChlorineDecay");
    var label = document.getElementById("label-chlorine");
    var startingParticles = document.getElementById("starting-particles-free-chlorine-concentration-chlorine");
    var injectedParticles = document.getElementById("injected-particles-free-chlorine-concentration-chlorine");

    if (checkBox.checked == true) {
        label.style.display = "block";
        startingParticles.required = true;
        injectedParticles.required = true;
    } else {
        label.style.display = "none";
        startingParticles.required = false;
        injectedParticles.required = false;
    }
}

function groupByTimestepCheckAll() {
    
    var checkBox = document.getElementById("flexCheckGroupByTimestep");
    var label = document.getElementById("label-groupby");
    var groupSize = document.getElementById("timestep-group-size");

    if (checkBox.checked == true){
        label.style.display = "block"
        groupSize.required = true
    }
    else {
        label.style.display = "none"
        groupSize.required = false
    }
}

function disableText() {

    var uploadButton = document.getElementById("upload-submit");
    var loadingButton = document.getElementById("upload-loading");
    var uploadButtonSettings = document.getElementById("settings-submit");
    var loadingButtonSettings = document.getElementById("settings-loading");

    uploadButton.style.display = "none";
    loadingButton.style.display = "block";
    uploadButtonSettings.style.display = "none";
    loadingButtonSettings.style.display = "block";

//     setInterval(function() {
//     fetch("static/update-text.txt")
//     .then(function (res) {
//         return res.text();
//     })
//     .then(function (data) {
//         console.log(data);
//         document.getElementById("text-show").innerHTML = data;
//     });
// }, 2000)
}