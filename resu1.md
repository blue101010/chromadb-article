```bash
import chromadb
import uuid

client = chromadb.Client()

collection = client.create_collection(name="policies")

with open("policies.txt", "r", encoding="utf-8") as f:
    policies: list[str] = f.read().splitlines()


collection.add(
    ids=[str(uuid.uuid4()) for _ in policies],
    documents=policies,
    metadatas=[{"line": line} for line in range(len(policies))],
)

print(collection.peek())

```



```bash
$ source myvenv
Virtual environment '.venv' is active.
(.venv) (.venv) 
ful70@L MINGW64 /c/DATA/GIT/chromadb (master)
$  python main.py 
{'ids': ['0d07bf7e-86ea-440b-a308-672044c2e2a6', 'b17bedb6-cacf-4c66-aee0-fb70a8201dfd', 'b18ac5c0-8c35-4117-b6f2-f0a5e012a144', 'bdceb86b-327e-4e6b-a4d0-ef8b195a164c', 'b5d49e54-370c-4897-9b07-6f90b8b0ec38', '94018412-05c6-407a-9016-01ca0242b80c', 'da309059-9be6-4ea1-91ea-b7d15ad3fe4d', '111fc9bf-151a-4a0c-9864-fcbe57dd49ff', '618bd603-561d-4f7e-9f24-5b5b2b46a27f', '642999a9-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
       [ 2.38607991e-02, -1.90459974e-02,  8.97545740e-03, ...,
         1.17223151e-02, -2.13582087e-02,  3.28621455e-02],
       ...,
-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
       [ 2.38607991e-02, -1.90459974e-02,  8.97545740e-03, ...,
         1.17223151e-02, -2.13582087e-02,  3.28621455e-02],
-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
       [ 2.38607991e-02, -1.90459974e-02,  8.97545740e-03, ...,
-c7bc-44d4-9910-c4c7c452b54b'], 'embeddings': array([[-7.53914043e-02,  4.95798923e-02,  1.36388307e-02, ...,
        -1.04128130e-01,  7.62689337e-02, -1.99265927e-02],
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
       [ 1.04567921e-02, -3.36727947e-02,  3.77094150e-02, ...,
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
        -3.12394984e-02, -2.69017578e-03,  4.41647135e-02],
       [ 2.38607991e-02, -1.90459974e-02,  8.97545740e-03, ...,
       [ 2.38607991e-02, -1.90459974e-02,  8.97545740e-03, ...,
         1.17223151e-02, -2.13582087e-02,  3.28621455e-02],
         1.17223151e-02, -2.13582087e-02,  3.28621455e-02],
       ...,
       ...,
       [ 2.43164562e-02,  2.15256996e-02,  4.44733836e-02, ...,
        -5.02046384e-02,  3.29509610e-03, -2.69088019e-02],
       [-7.34085962e-02,  2.64389906e-02, -1.92151200e-02, ...,
         3.25029045e-02,  1.85853139e-01, -1.20117124e-02],
       [-2.09288988e-02, -7.13527334e-05,  6.51416415e-03, ...,
        -1.27441548e-02,  1.59561411e-02,  2.43129861e-02]],
      shape=(10, 384)), 'documents': ['All garments are inspected for quality before being packaged for shipment to ensure they meet our craftsmanship and durability standards.', 'Standard domestic shipping takes 3–5 business days after your order has been processed and handed to the carrier.', 'Expedited domestic shipping delivers within 1–2 business days for orders placed before 1 p.m. local warehouse time.', 'International shipping is available to over 200 destinations, with transit times varying by region and carrier service level.', 'Customers are responsible for any local duties, taxes, or import fees assessed by customs authorities in their country.', 'Orders over 75 dollars qualify for free standard shipping within eligible domestic regions, before taxes and discounts are applied.', 'Every shipment includes a tracking number emailed to the address provided at checkout once the carrier scans the package.', 'We offset 100 percent of shipping‑related carbon emissions by investing in verified environmental and reforestation projects.', 'Packaging materials are made from 100 percent recycled or sustainably sourced paper, cardboard, and biodegradable inks.', 'We offer a 30‑day return window starting from the delivery date as confirmed by carrier tracking information.'], 'uris': None, 'included': ['metadatas', 'documents', 'embeddings'], 'data': None, 'metadatas': [{'line': 0}, {'line': 1}, {'line': 2}, {'line': 3}, {'line': 4}, {'line': 5}, {'line': 6}, {'line': 7}, {'line': 8}, {'line': 9}]}
(.venv) (.venv)
ful70@L MINGW64 /c/DATA/GIT/chromadb (master)
```