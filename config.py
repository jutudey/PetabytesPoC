

# this page contains the configuration for the app


app_name = "Petabytes v0.6"

data_folder = 'data'

required_files_description = [['ezyVet Invoice Lines',
                                   'Invoice Lines Report',
                                   'Invoice_Lines_Report-',
                                   'Go to ezyVet https://gvak.euw1.ezyvet.com/?recordclass=Reporting&recordid=0 and click on "Invoice Lines Report" in the File column'],
                                  ['ezyVet Animals Report',
                                   'Animals Report',
                                   'Animals_Report-',
                                   'Go to ezyVet https://gvak.euw1.ezyvet.com/?recordclass=Reporting&recordid=0 and click on "Animals Report" in the File column'],
                                  # ['ezyVet Wellness Plan Report',
                                  #  'WellnessPlanMembership_Export',
                                  #  'WellnessPlanMembership_Export',
                                  #  'Go to ezyVet https://gvak.euw1.ezyvet.com/# and follow the instructions to export the Wellness Plan Memberships.'],
                                  ['VERA Payment History',
                                   'payment-history-', 'payment-history-',
                                   'Go to VERA Toolbox https://app.gardenvets.com/adad4b9d-8ad5-4ef4-9f3f-7916b0850882/reports/report-list and click on "Payment History" in the File column'],
                                  # ['VERA Adyen Payment Links',
                                  #  'paymentLinks',
                                  #  'paymentLinks',
                                  #  'Go to VERA Toolbox https://app.gardenvets.com/adad4b9d-8ad5-4ef4-9f3f-7916b0850882/reports/report-list and click on "Payment History"'],
                                  ['VERA Pet Care Plans',
                                   'pet-care-plans-',
                                   'pet-care-plans-',
                                   'Go to VERA Toolbox https://app.gardenvets.com/adad4b9d-8ad5-4ef4-9f3f-7916b0850882/reports/report-list and click on "PetCare Plans"]']
                                  ]

# Filename Prefix
invoice_lines_prefix = 'Invoice_Lines_Report-'
non_approved_invoice_lines_prefix = 'evNonApprovedInvoiceLines-'

# allocation of staff to roles
vets = [
    "Amy Gaines", "Kate Dakin", "Ashton-Rae Nash", "Sarah Halligan",
    "Hannah Brightmore", "Kaitlin Austin", "James French", "Joshua Findlay", "Andrew Hunt", "Georgia Cleaton",
    "Alan Robinson", "Sheldon Middleton", "Horatio Marchis", "Sara Jackson"
]

locums = ["Laura Troth", "Claire Hodgson"]

students = ["Megan Perkins", "Neil Jones", "Yifan Guo"]

cops = [
    "System", "Setup", "Jennifer Hammersley", "Hannah Pointon", "Sheila Rimes",
    "Victoria Johnson", "Linda Spooner", "Amy Bache", "Katie Goodwin", "Catriona Bagnall", "Francesca James",
    "Katie Jones", "Emily Freeman", "Esmee Holt", "Charlotte Middleton", "Maz Darley"
]

nurses = [
    "Zoe Van-Leth", "Amy Wood", "Charlotte Crimes", "Emma Foreman",
    "Charlie Hewitt", "Hannah Brown", "Emily Castle", "Holly Davies", "Liz Hanson",
    "Emily Smith", "Saffron Marshall", "Charlie Lea-Atkin", "Amber Smith", "Katie Jenkinson",
    "Nicky Oakden"
]

cats = ["C1V", "C2V", "C3V"]
dogs = ["D1V", "D2V", "D3V"]
rabbits_ferrets = ["S1V", "S2V", "S3V"]
small_furries = ["SF1", "SF2", "SF3"]
complex_cases = ["CX1", "CX2", "CX3"]
petcare_advanced = ['PCA']
