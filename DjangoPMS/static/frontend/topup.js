const credit = document.getElementById("credits");
const updated_credits = document.getElementById("credit_tally")

credit.addEventListener("input", updateValue)
function updateValue(e){
    updated_credits.textContent = "£" + credit.value / 100;
}