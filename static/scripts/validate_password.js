const myInput = document.getElementById("user_pass");
const letter = document.getElementById("letter");
const capital = document.getElementById("capital");
const number = document.getElementById("number");
const specialCharacters = document.getElementById("special_char");
const length = document.getElementById("length");

myInput.onfocus = function() {
  document.getElementById("message").style.display = "block";
}

myInput.onblur = function() {
  document.getElementById("message").style.display = "none";
}

myInput.onkeyup = function() {
  const lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {
    letter.classList.toggle("invalid");
    letter.classList.toggle("valid");
  }

  const upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {
    capital.classList.toggle("invalid");
    capital.classList.toggle("valid");
  }

  const numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {
    number.classList.toggle("invalid");
    number.classList.toggle("valid");
  }

   const characters = /[*!@$%^&\(\)\{\}\[\]:;<>,.\?/~_-]/g; // //g flag - global
  if(myInput.value.match(characters)) {
    specialCharacters.classList.toggle("invalid");
    specialCharacters.classList.toggle("valid");
  }

  if(myInput.value.length >= 8 && myInput.value.length <= 16) {
    length.classList.toggle("invalid");
    length.classList.toggle("valid");
  }
}