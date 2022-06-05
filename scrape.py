import requests
from bs4 import BeautifulSoup

def get_properties_for_page(page_number):
    page = requests.get("https://www.property24.com/for-sale/cape-town/western-cape/432/p" + str(page_number))
    
    if page.status_code != 200:
        print("Bad status code: " + str(page.status_code))
        exit(1)

    soup = BeautifulSoup(page.text, 'html.parser')

    def extract_value(tag):
        value = None
        if tag is not None:
            value = tag.contents[0].strip().replace('\xa0', '')

        return value
    
    def extract_property_type_value(tag):
        value = extract_value(tag)
        if value is None:
            return None
        
        start_index = 0
        end_index = len(value)
        
        bedroom_index = value.find("Bedroom")
        
        if bedroom_index > -1:
            start_index = bedroom_index + 8
            
        in_index = value.find("For Sale")
        if in_index > -1:
            end_index = in_index - 1
        else:  
            in_index = value.find("in")
            if in_index > -1:
                end_index = in_index - 1
            
        return value[start_index:end_index]
        

    def get_properties(tag):
        properties = []
        for x in tag:
            id = x['data-listing-number']
            price = None
            price_tag = x.find(class_='p24_price')
            d = price_tag.attrs
            if "content" in d:
                price = price_tag['content']
            else:
                price = extract_value(x.find(class_='p24_price'))
            location = extract_value(x.find(class_='p24_location'))
            address = extract_value(x.find(class_='p24_address'))
            property_type = extract_property_type_value(x.find(class_='p24_description'))
            if property_type is None:
                property_type = extract_property_type_value(x.find(class_='p24_title'))
                
            size_tag = x.find(class_='p24_size')
            size = None
            if size_tag is not None:
                size = extract_value(size_tag.contents[3])
            features = x.find_all(class_='p24_featureDetails')
            p = {
                'id': id,
                'price': price,
                'location': location,
                'address': address,
                'size': size,
                'property_type': property_type
            }
            for f in features:
                feature_name = f['title']
                feature_value = f.span.contents[0]
                p[feature_name] = feature_value

            properties.append(p)
        return properties

    promoted = get_properties(soup.find_all(class_='p24_promotedTile'))
    regular = get_properties(soup.find_all(class_='p24_regularTile'))

    return promoted + regular

all_properties = []

for i in range(1, 441):
    print(i)
    all_properties.extend(get_properties_for_page(i))

print(len(all_properties))
print(all_properties[0])

