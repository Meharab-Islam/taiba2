function printPage() {
    var printContent = document.body.innerHTML;
    var originalContent = document.body.innerHTML;

    // Open a new window for print preview
    var printWindow = window.open('', '_blank');
    
    // Set the content of the new window to the original content
    printWindow.document.write(printContent);

    // Add a button for printing in the new window
    printWindow.document.write('<button onclick="window.print()">Print</button>');

    // Close the original content window
    document.body.innerHTML = originalContent;

    // Focus on the new window for print preview
    printWindow.focus();
}
