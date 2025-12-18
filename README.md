<h1>DefenderData Time Entry</h1>
  <p>This script is intended to reduce time attorneys spend entering time on DefenderData by utilizing reports from existing CRM software.</p>
  <p>Many attorneys are already entering billable time in their firm's CRM software, <i>e.g. MyCase and Cleo</i>, so in an effort to reduce the double entry this script can be used in conjunction with built in reporting features in the CRM software.</p>

<h3>The time entry data file:</h3>
<p>This file is to be read in by the script for the purposes of processing data.</p>
<p>Currently, the script is set up for the MyCase report "User time & expenses" to be exported as a CSV (Clio support coming soon).</p>
<p>The file is parsed to only include the relevant columns in order: 
  <ul>
    <li>Date</li>
    <li>Activity</li>
    <li>Duration/Quantity</li>
    <li>Case Number</li>
    <li>Description</li>
  </ul>
</p>

<h3>Browser interaction:</h3>
<p>The script will open a browser and browse to the URL of the DefenderData website, then automatically log in to the attorney's account that is being used.</p>
<p>Once successfully logged in to the website, it clicks on the time sheet and begin entering the rows of data until we reach the end of the time entry list.</p>

<h3>Timesheet Entries:</h3>
<p>During the data entry of the time sheet the script is checking that each element is present and interactable on the page before attempting to put data inside the field.</p>
<p>For each row, one of two things will happen, if the row is successful it is logged in a successful log file timestamped with the current date on it.</p>
<p>Should the entry fail for any reason, <i>(the site is lagging, a case number wasn't found in the system, etc.)</i> then the error is caught, handled, and logged into a specific error log file. <br>In addition, we also write the time entry as it was originally provided from the CRM to a "failure" CSV file, so we can reimport when the errors have been corrected without dealing with duplicate data from the original CSV containing time entries.</p>

<h2>Conclusion</h2>
<p>Using this script, I've been able to cut 3-4 hours of work per attorney at the end of each month down to about 5 minuntes setting up the script and letting it run.</p>
<p>Hopefully, I can expand this to more attorneys and other CRMs to help out even more attornies with their end of month billing.</p>
