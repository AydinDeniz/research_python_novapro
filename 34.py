import requests
from bs4 import BeautifulSoup
from scapy.all import *
import re
import openai

# Set up OpenAI API key
openai.api_key = 'your_openai_api_key'

# Function to scan for SQL Injection vulnerability
def scan_sql_injection(url):
    payloads = ["' OR 1=1 --", "' OR '1'='1"]
    for payload in payloads:
        response = requests.get(url + payload)
        if "error" in response.text.lower():
            return True
    return False

# Function to scan for XSS vulnerability
def scan_xss(url):
    payloads = ["</script><script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
    for payload in payloads:
        response = requests.get(url + payload)
        if payload in response.text:
            return True
    return False

# Function to scan for CSRF vulnerability
def scan_csrf(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    forms = soup.find_all('form')
    for form in forms:
        if 'csrf' not in form.get('action', '').lower() and 'csrf' not in form.get('method', '').lower():
            return True
    return False

# Function to suggest remediation steps using GPT-4
def suggest_remediation(vulnerability):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Suggest remediation steps for the following web application vulnerability: {vulnerability}\n\nRemediation steps:",
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Main function to scan web application
def scan_web_application(url):
    vulnerabilities = []
    
    if scan_sql_injection(url):
        vulnerabilities.append("SQL Injection")
    
    if scan_xss(url):
        vulnerabilities.append("XSS")
    
    if scan_csrf(url):
        vulnerabilities.append("CSRF")
    
    remediation_steps = {}
    for vulnerability in vulnerabilities:
        remediation_steps[vulnerability] = suggest_remediation(vulnerability)
    
    return vulnerabilities, remediation_steps

# Example usage
url = "http://example.com"
vulnerabilities, remediation_steps = scan_web_application(url)
print("Detected Vulnerabilities:", vulnerabilities)
print("Remediation Steps:")
for vulnerability, steps in remediation_steps.items():
    print(f"{vulnerability}: {steps}")