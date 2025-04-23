import os
import html

import resend

resend.api_key = os.getenv('RESEND_API_KEY')

receivers = [
    'nhann@ohseoulhappy.com',
    'dev.kartikaggarwal117@gmail.com'
]


def send_email(body, to=receivers):
    params: resend.Emails.SendParams = {
        'from': 'Update Notification <dev@kartikcodes.in>',
        'to': to,
        'subject': 'Scraped Products',
        'html': body
    }

    return resend.Emails.send(params)


"""
{
    "choicemusicla": [
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        ...
    ],
    "musicplaza": [
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        {
            "Source URL": "...",
            "Shopify admin URL": "...",
        },
        ...
    ],
    ...
}
"""
def prepare_email(updated_data):
    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="UTF-8">',
        '<style>',
        '  table { border-collapse: collapse; width: 100%; }',
        '  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
        '  th { background-color: #f2f2f2; }',
        '  a { color: #1a0dab; text-decoration: none; }',
        '</style>',
        '</head>',
        '<body>',
        '<h1>Scraped Products Summary</h1>'
    ]

    for site_name, products in updated_data.items():
        escaped_site = html.escape(site_name)
        html_parts.append(f'<h2>{escaped_site}</h2>')
        html_parts.append('<table>')
        html_parts.append(
            '<tr>'
            '<th>Source URL</th>'
            '<th>Shopify Admin URL</th>'
            '</tr>'
        )
        for item in products:
            src = html.escape(item['Source URL'])
            shop = html.escape(item['Shopify Admin URL'])
            html_parts.append(
                '<tr>'
                f'<td><a href="{src}">{src}</a></td>'
                f'<td><a href="{shop}">{shop}</a></td>'
                '</tr>'
            )
        html_parts.append('</table>')

    html_parts.extend(['</body>', '</html>'])

    return '\n'.join(html_parts)