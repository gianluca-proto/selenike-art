from services.cloudinary_service import get_resources

# Scegli il prefisso che vuoi testare (ad esempio 'img/banner/')
prefisso = 'img/banner/'
risorse = get_resources('image', prefisso)

print(f"Risorse trovate per '{prefisso}':")
for img in risorse:
    print(f"public_id: {img['filename']} | url: {img['url']}")

if risorse:
    print(f"\nURL prima immagine: {risorse[0]['url']}")
    print("Copia questo URL nel browser per visualizzare l'immagine.")
else:
    print("Nessuna immagine trovata per questo prefisso.")

