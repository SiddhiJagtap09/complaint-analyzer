// Complaint Form Validation
function validateComplaintForm() {
  const typeInput = document.getElementById('complaint_type_input');
  const areaInput = document.getElementById('area_input');
  const desc = document.querySelector('textarea[name="description"]');

  // Complaint type only letters and spaces
  const typeRegex = /^[A-Za-z\s]+$/;

  if (!typeRegex.test(typeInput.value.trim())) {
    alert("Complaint type must contain only letters.");
    typeInput.focus();
    return false;
  }

  if (!areaInput.value.trim()) {
    alert("Please enter area.");
    areaInput.focus();
    return false;
  }

  if (!desc.value.trim()) {
    alert("Please enter description.");
    desc.focus();
    return false;
  }

  return true;
}
