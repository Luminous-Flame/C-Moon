<%

import sys
import csv
import logging

log = logging.getLogger(__name__)

cols = [
    {"title": "Host Name", "id": "name", "visible": True, "field": lambda h: h.get('name', '')},
    {"title": "OS", "id": "os", "visible": True, "field": lambda h: h['ansible_facts'].get('ansible_distribution', '') + ' ' + h['ansible_facts'].get('ansible_distribution_version', '')},
    {"title": "IP", "id": "ip", "visible": True, "field": lambda h: h['ansible_facts'].get('ansible_default_ipv4', {}).get('address', '')},
    {"title": "MAC", "id": "mac", "visible": True, "field": lambda h: h['ansible_facts'].get('ansible_default_ipv4', {}).get('macaddress', '')},
    {"title": "CPU", "id": "cpu", "visible": True, "field": lambda h: str(h['ansible_facts'].get('ansible_processor', [''])[2]) if h['ansible_facts'] and h['ansible_facts'].get('ansible_processor') else ''},
    {"title": "CPU Core", "id": "core", "visible": True, "field": lambda h: int(h['ansible_facts'].get('ansible_processor_cores', 0)) if h['ansible_facts'] and h['ansible_facts'].get('ansible_processor_cores') else 0},
    {"title": "CPU Count", "id": "cpu_cnt", "visible": True, "field": lambda h: int(h['ansible_facts'].get('ansible_processor_count', 0)) if h['ansible_facts'] and h['ansible_facts'].get('ansible_processor_count') else 0},
    {"title": "Total Core", "id": "core_total", "visible": True, "field": lambda h: int(h['ansible_facts'].get('ansible_processor_count', 0) or 0) * int(h['ansible_facts'].get('ansible_processor_cores', 0) or 0)},
    {"title": "Threads per core", "id": "threads_per_core", "visible": True, "field": lambda h: int(h['ansible_facts'].get('ansible_processor_threads_per_core', 0))},
    {"title": "Threads Total", "id": "threads_total", "visible": True, "field": lambda h: int(h['ansible_facts'].get('ansible_processor_vcpus', 0))},
    {"title": "Memory", "id": "mem", "visible": True, "field": lambda h: '%0.0f' % (int(h['ansible_facts'].get('ansible_memtotal_mb', 0)) / 1000.0)},
    {"title": "Vendor", "id": "vendor", "visible": True, "field": lambda h: str(h['ansible_facts'].get('ansible_chassis_vendor', ''))},
    {"title": "Product Name", "id": "prodname", "visible": True, "field": lambda h: str(h['ansible_facts'].get('ansible_product_name', ''))},
    {"title": "Serial No", "id": "serial", "visible": True, "field": lambda h: str(h['ansible_facts'].get('ansible_product_serial', ''))}
]

# Enable columns specified with '--columns'
if columns is not None:
  for col in cols:
    if col["id"] in columns:
      col["visible"] = True
    else:
      col["visible"] = False

def get_cols():
  return [col for col in cols if col['visible'] is True]

fieldnames = []
for col in get_cols():
  fieldnames.append(col['title'])

writer = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(fieldnames)
for hostname, host in hosts.items():
  if 'ansible_facts' not in host:
    log.warning(u'{0}: No info collected.'.format(hostname))
  else:
    out_cols = []
    for col in get_cols():
      out_cols.append(col['field'](host))
    writer.writerow(out_cols)
%>
