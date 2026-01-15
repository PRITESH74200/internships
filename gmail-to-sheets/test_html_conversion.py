from bs4 import BeautifulSoup
import re

html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1" />

 <title>Executive Search Consultancy</title>

 <style>
 /* RESET */
 body {
 margin: 0 !important;
 padding: 0 !important;
 background: #ffffff !important;
 -webkit-text-size-adjust: 100%;
 -ms-text-size-adjust: 100%;
 font-family: Arial, sans-serif;
 }

 table {
 border-spacing: 0 !important;
 border-collapse: collapse !important;
 }

 img {
 border: 0;
 display: block;
 max-width: 100%;
 }

 /* CONTAINER */
 .wrapper {
 width: 100%;
 table-layout: fixed;
 background-color: #ffffff;
 padding-bottom: 20px;
 }

 .container {
 max-width: 600px;
 width: 100%;
 margin: 0 auto;
 background: #ffffff;
 border: 1px solid #ececec;
 }

 .content {
 padding: 20px 24px;
 font-size: 15px;
 line-height: 1.5;
 color: #000000;
 }

 /* CTA BUTTON */
 .cta-btn {
 background: #1F4BFF !important;
 color: #ffffff !important;
 padding: 12px 22px;
 font-size: 15px;
 font-weight: bold;
 border-radius: 6px;
 text-decoration: none;
 display: inline-block;
 text-align: center;
 box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.15);
 }

 /* MOBILE */
 @media only screen and (max-width: 600px) {
 .content {
 padding: 18px !important;
 }

 p {
 font-size: 14px !important;
 }

 .cta-btn {
 width: 100% !important;
 padding: 14px 0 !important;
 display: block !important;
 font-size: 16px !important;
 }
 }
 </style>
</head>

<body>

 <span style="display:none;opacity:0;visibility:hidden;">Skill Scout Consultancy</span>

 <table role="presentation" class="wrapper" width="100%">
 <tr>
 <td align="center">

 <table role="presentation" class="container">
 <tr>
 <td class="content">

 <p style="margin:0 0 12px;">Dear Pritesh,</p>

 <p style="margin:0 0 12px;">
 I hope you're doing well. I just reviewed your profile for an urgent opportunity of <b>Fresher</b> with a top company, and your experience seems like an excellent match.</p>
<p style="margin:0 0 12px;">
 Your profile is currently in the review stage for the next shortlist round, and it looks like a promising fit. Before I share your CV with the hiring manager, I just need a quick confirmation of a few details.</p>
<p style="margin:0 0 12px;">
 This step takes <b>less than 30 seconds,</b> and updating it now will help us move your application into the <b>priority shortlist</b> for the client.
 </p>

 <p style="margin:18px 0 8px; font-weight:bold;"><strong>About Us:</strong></p>

 <p style="margin:0 0 16px;">
 We serve as a trusted platform designed to keep professionals connected with real and relevant job opportunities. Our purpose is to ensure that every candidate's profile stays updated, visible, and aligned with the evolving needs of employers across industries.</p>
 <p style="margin:0 0 16px;">
 By simplifying the process and maintaining a transparent approach, we help candidates take the right step toward advancing their careers while ensuring they are always ready when the next opportunity comes their way.

 </p>

 <p style="margin:0 0 18px;">
 To proceed, please take a moment to update your information using the link below:
 </p>

 <!-- CTA BUTTON -->
 <table role="presentation" width="100%" style="margin: 16px 0;">
 <tr>
 <td align="left">
 <a href="http://delivery.jobs.shine.com/FDTJAOP?id=37602" class="cta-btn">
 Update My Profile
 </a>
 </td>
 </tr>
 </table>

 <p style="margin:0 0 16px;">
 Once you've updated it, our screening team will verify the details and immediately connect you with the recruiter managing this role.
 </p>

<p style="margin:0 0 -4px;">
 Looking forward to moving your application to the next round.

 </p>

 <img src="https://images.konnectmail.com/skillscoutlogo.png"
 alt="logo" width="100" style="margin: 0 0 -2px;" />
 <p style="margin:0; padding: 0;">
 Warm regards,<br>
 <strong>Anjali Kapoor</strong><br>
 Senior Recruiter | Skill Scout Consultancy
 </p>

 </td>
 </tr>
 </table>

 </td>
 </tr>
 </table>

</body>

</html>"""

# Apply the same conversion logic as email_parser.py
soup = BeautifulSoup(html, 'html.parser')

# Remove script and style elements
for script in soup(['script', 'style']):
    script.decompose()

# Get text
text = soup.get_text()

# Clean up whitespace (matching email_parser.py logic)
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)

print("=" * 80)
print("PLAIN TEXT OUTPUT (as it appears in Google Sheets):")
print("=" * 80)
print(text)
print("=" * 80)
