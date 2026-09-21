import streamlit as st
from config import data_path
from glob import glob
import cv2
from pkg.microsocpy_algs import vizu_image, otsu_threshold
def order_dict(d, order= ["DAPI", "RED", "GREEN"]):
    return {k: d[k] for k in order if k in d}

def main():
    ## take full width of the page
    st.set_page_config(layout="wide")
    cols = st.columns(3)
    concentration = cols[0].selectbox("Choose a concentration", ["0", "5", "10"])
    exposure = cols[1].selectbox("Choose a exposure time", ["24h", "48h"])
    field = cols[2].selectbox("Choose a Aperture", ["1","2"])
    images = glob(str(data_path / f"3t3-{exposure}-{concentration}-*-{field}.tif"))
    ## show one example for image contain DAPI, RED or GREEN in title
    examples = {}
    for img in images:
        if "dapi" in img:
            examples["DAPI"] = img
        elif "red" in img:
            examples["RED"] = img
        elif "green" in img:
            examples["GREEN"] = img
    st.write("Examples found:")
    ## put the three images on the same row
    cols = st.columns(4)
    
    luminosity = st.slider("Pick a luminosity", 0, 20000, 100)
    for i, (key, img) in enumerate(order_dict(examples).items()):
        processed_img = vizu_image(img, luminosity)
        cols[i].image(processed_img, caption=f"{key} processed at {luminosity}%")
    merged_image = cv2.addWeighted(vizu_image(examples["GREEN"], luminosity), 1, vizu_image(examples["RED"], luminosity), 1, 0)
    cols[3].image(merged_image, caption="Merged image")
    ## show the otsu thresholding for each image
    st.write("Otsu thresholding:")
    cols = st.columns(4)
    for i, (key, img) in enumerate(order_dict(examples).items()):
        processed_img = vizu_image(img, luminosity)
        otsu_img = otsu_threshold(img, luminosity)
        cols[i].image(otsu_img, caption=f"{key} Otsu thresholding")
    merged_otsu = otsu_threshold([examples["GREEN"], examples["RED"]], luminosity)
    cols[3].image(merged_otsu, caption="Merged image Otsu thresholding")

    ## add algorithm to draw cells boundaries
    st.write("Segmentation algorithms:")
    algo = st.selectbox("Choose an algorithm", ["Contour"])
    cols = st.columns(4)
    for i, (key, img) in enumerate(order_dict(examples).items()):
            processed_img = vizu_image(img, luminosity)
            otsu_img = otsu_threshold(img, luminosity)
            ## find contours
            contours, _ = cv2.findContours(otsu_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            ## draw contours
            otsu_img = cv2.cvtColor(otsu_img, cv2.COLOR_GRAY2BGR)
            contour_img = cv2.drawContours(otsu_img, contours, -1, (255, 87, 35), 3)
            cols[i].image(contour_img, caption=f"{key} Contour")
    contours, _ = cv2.findContours(merged_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_img = cv2.cvtColor(merged_otsu, cv2.COLOR_GRAY2BGR)
    merged_contour = cv2.drawContours(contour_img, contours, -1, (255, 87, 35), 3)
    
    cols[3].image(merged_contour, caption="Merged image Contour")
if __name__ == "__main__":
    main()