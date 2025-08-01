import pandas as pd

# Taxonomy mapping
taxonomy = {
    "Account Creation": [
        """How do I sign up for a new account on your site?""",
        """I tried making an account but it says 'email already used,' what should I do?""",
        """Need help creating an account for my dad, can I do it under my email?""",
        """I was trying to make an account for my cousin but it wouldn't let me, maybe because we share a laptop?""",
        """Can I sign up without giving my phone number?""",
        """Made a profile yesterday but can't tell if it went through, nothing in my email."""
    ],
    "Login Issues": [
        """I can't log in even though my password is correct.""",
        """Every time I try logging in, it kicks me back to the home page.""",
        """My account just logged me out randomly and now I can't get back in.""",
        """Whenever I try to log in on my work computer it just refreshes, but my phone works fine.""",
        """Is there a reason I keep getting kicked out after like 5 mins?""",
        """My login works for my brother but not for me on the same device??"""
    ],
    "Password Reset": [
        """I forgot my password and the reset email never came.""",
        """Trying to reset password but the link expired in 2 minutes??""",
        """How can I change my password without logging in?""",
        """I clicked reset password but the link is broken—might be my email client though.""",
        """I think I changed my password but now none of my usual ones work.""",
        """I don't remember if I signed up with Facebook or email, how do I reset my pass?"""
    ],
    "Two-Factor Authentication": [
        """My 2FA code is not working, keeps saying invalid.""",
        """I lost my phone with the authentication app on it, how do I log in?""",
        """Can I disable two-factor temporarily? I'm traveling and can't get texts.""",
        """I got a new phone yesterday and now can't log in—does 2FA need to be re-set up?""",
        """The code you sent is different every time I try, is that normal?""",
        """I was traveling and didn't have signal, so I couldn't get my login code… now I'm locked out."""
    ],
    "Profile Updates": [
        """How do I update my profile picture?""",
        """I need to change my email from Gmail to Outlook but can't find the option.""",
        """Accidentally put wrong birthday on my profile, can you fix it?""",
        """My profile name shows twice on my account, can you fix that?""",
        """I need to switch my email, but the system says 'already in use' even though I own it.""",
        """Changed my profile pic but it's blurry now.""",
    ],

    "Billing Inquiry": [
        """Why was I charged twice this month?""",
        """My credit card shows a payment I didn't make.""",
        """Can you explain the $4.99 fee that appeared yesterday?""",
        """There's a random $2.00 charge this morning—no idea what it's for.""",
        """I was charged on two different cards this month (same account).""",
        """Got a charge a week before my renewal date—why?""",
    ],

    "Refund Request": [
        """Can I get a refund for my subscription?""",
        """I canceled before renewal but still got billed—need refund.""",
        """Bought wrong plan by accident, please refund.""",
        """The subscription renewed right after I paused it, need my money back.""",
        """I accidentally bought the wrong product twice.""",
        """Paid for premium but only got the free version—refund please.""",
    ],

    "Subscription Upgrade/Downgrade": [
        """How can I switch to the annual plan?""",
        """Want to downgrade from premium to basic, what's the process?""",
        """Accidentally upgraded my subscription, how do I revert?""",
        """How do I check if I'm actually on the yearly plan now?""",
        """Wanted to upgrade but it says 'payment declined' even though I have funds.""",
        """Downgraded my plan but still got charged the higher amount.""",
    ],

    "Payment Method Update": [
        """How do I change my payment card?""",
        """My card expired, need to update payment info.""",
        """Can I pay via PayPal instead of credit card?""",
        """My card got stolen, need to switch to a new one ASAP.""",
        """Is there a way to use two cards for payment?""",
        """Tried to change payment but it just spins forever on the loading screen.""",
    ],

    "Invoice Request": [
        """Need a copy of last month's invoice for my accountant.""",
        """Can you send me all my invoices for this year?""",
        """Lost my receipt for March, please resend.""",
        """Need a detailed receipt for tax purposes—does it show VAT?""",
        """Could you resend me invoices from last year? I think I deleted them.""",
        """Can you add my company name to the invoice after it's been issued?""",
    ],

    "Order Status": [
        """Where is my order #12456?""",
        """Can you tell me when my chair will arrive?""",
        """I placed an order two weeks ago, no updates yet.""",
        """Ordered something last Friday but didn't get a confirmation email.""",
        """Tracking says 'label created' for days—what's going on?""",
        """Do you guys ship on weekends?""",
    ],

    "Shipping Delay": [
        """My package is late, tracking says 'in transit' for 5 days.""",
        """Why is my delivery stuck in another city?""",
        """I paid for express shipping but it's still not here.""",
        """Package was supposed to come yesterday but no updates since Monday.""",
        """Says delivered but it's not here, maybe sent to the wrong address.""",
        """Paid extra for 2-day shipping but it's been a week.""",
    ],

    "Product Return": [
        """How do I return a defective item?""",
        """The shoes I got are the wrong size, want to return.""",
        """Is there a return label in the box or do I print one?""",
        """The item I got is not what I ordered—it's close, but not the same model.""",
        """I threw away the box, can I still return this?""",
        """I think my return was received but I haven't gotten a refund yet.""",
    ],

    "Warranty Claim": [
        """My headphones broke after 3 months, is it covered?""",
        """Can you replace my blender under warranty?""",
        """How long is the warranty on this product?""",
        """My laptop charger melted after 6 months—covered?""",
        """The stitching came apart on my bag after 2 weeks of light use.""",
        """Do you need photos for a warranty claim?""",
    ],

    "Technical Bug Report": [
        """The app crashes when I open settings.""",
        """I keep getting 'error 500' when logging in on desktop.""",
        """Notifications aren't working after the last update.""",
        """App freezes when I try to upload certain files (jpg is fine, png isn't).""",
        """It says 'no internet' even though I'm connected.""",
        """My cursor disappears only in your desktop app.""",
    ],

    "Feature Request": [
        """Please add dark mode, my eyes hurt at night.""",
        """Any chance you can add calendar integration?""",
        """Would love to have a widget for quick access.""",
        """Could you add an 'undo' button to edits?""",
        """Would love if you had more font choices for reports.""",
        """Is there a way to make the dashboard less cluttered?""",
    ],

    "Integration Help": [
        """How do I connect this to Google Calendar?""",
        """I linked my account to Slack but it's not syncing.""",
        """Need help integrating with Zapier.""",
        """Tried linking with Google Calendar but only half my events show up.""",
        """Zapier keeps throwing a '403' error on your integration.""",
        """Can I connect this to Trello somehow?""",
    ],

    "Data Export": [
        """How do I download all my account data?""",
        """Can you send me an export of my chat history?""",
        """Want to back up all my data before deleting account.""",
        """How do I export my chat logs but not the attachments?""",
        """I need all my order history in CSV format.""",
        """Do you offer automated weekly exports?""",
    ],

    "Security Concern": [
        """I think my account was hacked—saw activity I didn't do.""",
        """Got an email about login from another country, was that you?""",
        """My account email changed without me doing it.""",
        """Saw a login from a device I don't own—should I be worried?""",
        """I keep getting password reset emails I didn't request.""",
        """My account picture was changed without me doing it.""",
    ],

    "Terms of Service Question": [
        """What's your cancellation policy?""",
        """If I cancel mid-month, do I get money back?""",
        """Do you allow account sharing?""",
        """Is there a minimum commitment period for the subscription?""",
        """Can I transfer my account to someone else?""",
        """What happens if I break a rule in the TOS?""",
    ],

    "Privacy Policy Question": [
        """Do you sell personal data to advertisers?""",
        """What info do you collect when I log in?""",
        """How do I delete all my stored data?""",
        """Do you store my payment details?""",
        """Are chat messages encrypted end-to-end?""",
        """If I delete my account, is my data completely gone?""",
    ],

    "Compliance Inquiry": [
        """Are you GDPR compliant?""",
        """Do you follow CCPA rules for California residents?""",
        """Need info on HIPAA compliance for business use.""",
        """Does your service work for EU customers under GDPR rules?""",
        """Do you process data in the US only or overseas too?""",
        """Is your system ISO certified?""",
    ],

    "Accessibility Support": [
        """Do you support screen readers?""",
        """Your font is too small—can I increase it?""",
        """The color contrast makes it hard to read, any options?""",
        """Can I adjust keyboard shortcuts?""",
        """Is there a high-contrast mode for reports?""",
        """Can you add captions to your tutorial videos?""",
    ],

    "Language Support": [
        """Is the app available in Spanish?""",
        """Can I switch the interface to French?""",
        """Will you add Japanese support soon?""",
        """Do you have Brazilian Portuguese available?""",
        """Any chance of adding Mandarin soon?""",
        """Can I set different languages for different users?""",
    ],

    "Mobile App Issue": [
        """Android app keeps freezing on login screen.""",
        """My iPhone app crashes every time I upload a file.""",
        """The mobile app won't update past version 2.3.""",
        """App won't load past the splash screen.""",
        """Notifications on my Android only work when I open the app.""",
        """Downloaded the app again but it says my device isn't supported.""",
    ],

    "Desktop App Issue": [
        """The Windows version won't install.""",
        """Mac app says 'damaged file' when I open it.""",
        """Keeps asking for admin password every time I start it.""",
        """After installing, the app opens then closes immediately.""",
        """Can't drag and drop files into the desktop version.""",
        """Keeps asking me to reinstall every time I log in.""",
    ],

    "Email Notifications": [
        """I'm not receiving password reset emails.""",
        """All your emails are going to spam.""",
        """Can you turn off order confirmation emails?""",
        """Haven't received any emails from you since last month.""",
        """Email confirmations work for orders but not for password resets.""",
        """The unsubscribe button in your email doesn't work.""",
    ],

    "Marketing Preferences": [
        """How do I unsubscribe from promos?""",
        """I still get marketing emails even after opting out.""",
        """Can I only get important notifications?""",
        """I want only updates about product changes, no promos.""",
        """Stopped getting marketing emails but still get push notifications.""",
        """Is there a way to pause marketing emails for a month?""",
    ],

    "Beta Program Enrollment": [
        """How do I join the beta program?""",
        """Want early access to new features, what's the process?""",
        """Is beta available in my country?""",
        """How do I know if I'm accepted into the beta?""",
        """Joined beta but my account looks the same.""",
        """Will beta affect my current settings?""",
    ],

    "General Feedback": [
        """Just wanted to say the service is great!""",
        """Love your new design—it's much easier to use.""",
        """The last update was confusing, please make a guide.""",
        """Your support team is fast but the responses feel copy-paste.""",
        """Love the features, but app speed could be better.""",
        """The dark mode is nice, but some buttons are unreadable.""",
    ],
}

# Flatten into a dataframe
data = []
for category, queries in taxonomy.items():
    for query in queries:
        data.append({"query": query, "category": category})

df = pd.DataFrame(data)

# Use consistent quoting for all entries
df.to_csv("support_query_classification.csv", index=False, quoting=1)  # QUOTE_ALL