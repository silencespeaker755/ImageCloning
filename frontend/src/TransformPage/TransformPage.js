import React, { useState } from "react";
import { useQuery, useMutation } from "react-query";
import { useParams, useNavigate } from "react-router-dom";
import { Stage, Layer } from "react-konva";
import { Button } from "@material-ui/core";
import axios from "../setting";
import Rectangle from "./Rectangle";
import TransformIcon from "@material-ui/icons/Transform";
import Loading from "../components/Loading";
import TitleSection from "../components/TitleSection";

export default function TransformPage() {
  const { backgroundId, imageId } = useParams();
  const navigate = useNavigate();

  const [imageSize, setImageSize] = useState({
    height: 0,
    width: 0,
  });
  const [info, setInfo] = useState({});

  const [rectangles, setRectangles] = useState([]);
  const [selectedId, selectShape] = useState(null);

  const checkDeselect = (e) => {
    // deselect when clicked on empty area
    const clickedOnEmpty = e.target === e.target.getStage();
    if (clickedOnEmpty) {
      selectShape(null);
    }
  };

  const {
    data: image = { background: "", crop: "" },
    isError: isEventsError,
    isLoading: isEventsLoading,
    isFetching: isEventsFetching,
    refetch: refetchEvents,
  } = useQuery(
    "CroppedImageFetching",
    async () => {
      const data = await axios.get("/image", {
        params: { image_id: backgroundId },
        responseType: "blob",
      });
      let url = URL.createObjectURL(data.data);
      const img = new Image();
      img.src = url;
      img.onload = () => handleImageLoaded(img.height, img.width, img);

      const crop = await axios.get("/image", {
        params: { image_id: imageId },
        responseType: "blob",
      });
      let url2 = URL.createObjectURL(crop.data);
      const img2 = new Image();
      img2.src = url2;

      img2.onload = () =>
        handleImageLoaded(img2.height, img2.width, img2, true);
      return { background: url, crop: url2 };
    },
    {
      retry: false,
      onSuccess: (data) => {
        // console.log(data);
      },
    }
  );

  const { mutate: cloneImage, isLoading } = useMutation(
    async () => {
      const msg = await axios.post("/clone", {
        source_info: { id: imageId, ...info },
        dest_info: { id: backgroundId, ...imageSize },
      });
      return msg;
    },
    {
      retry: false,
      onSuccess: (msg) => {
        const { data } = msg;
        console.log("success!!");
        navigate(`/result/${data}`);
      },
      onError: (err) => {},
    }
  );

  const handleImageLoaded = (imageHeight, imageWidth, img, cropped = false) => {
    let height = imageHeight;
    let width = imageWidth;
    let scale = 1;
    let maximum = 700;
    if (cropped) maximum = 300;
    if (height > width) {
      scale = maximum / height;
      width = (width * maximum) / height;
      height = maximum;
    } else {
      scale = maximum / width;
      height = (height * maximum) / width;
      width = maximum;
    }
    if (cropped) {
      setRectangles([
        {
          x: 0,
          y: 0,
          width,
          height,
          fillPatternScaleX: scale,
          fillPatternScaleY: scale,
          fillPatternImage: img,
          // fill: "green",
        },
      ]);
    } else {
      setImageSize({
        height,
        width,
      });
    }
  };

  const handleTransform = () => {
    // console.log({
    //   source_info: { id: imageId, ...info },
    //   dest_info: { id: backgroundId, ...imageSize },
    // });
    cloneImage();
  };

  return (
    <div className="border-section">
      <TitleSection title="Cloning" />
      <div className="flex-all-center">
        <div
          style={{
            backgroundImage: `url(${image.background})`,
            backgroundSize: "cover",
            backgroundRepeat: "no-repeat",
          }}
        >
          <Stage
            width={imageSize.width}
            height={imageSize.height}
            onMouseDown={checkDeselect}
            onTouchStart={checkDeselect}
          >
            <Layer>
              {rectangles.map((rect, i) => {
                return (
                  <Rectangle
                    key={i}
                    shapeProps={rect}
                    isSelected={rect.id === selectedId}
                    onSelect={() => {
                      selectShape(rect.id);
                    }}
                    onChange={(newAttrs) => {
                      const rects = rectangles.slice();
                      rects[i] = newAttrs;
                      setRectangles(rects);
                    }}
                    setInfo={setInfo}
                  />
                );
              })}
            </Layer>
          </Stage>
        </div>
      </div>
      <div className="flex-all-center" style={{ marginTop: "30px" }}>
        {isLoading ? (
          <Loading />
        ) : (
          <Button
            variant="outlined"
            startIcon={<TransformIcon />}
            onClick={handleTransform}
          >
            Transform
          </Button>
        )}
      </div>
    </div>
  );
}
