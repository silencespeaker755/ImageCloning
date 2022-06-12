import React, { useEffect, useRef } from "react";
import { Rect, Transformer } from "react-konva";

export default function Rectangle({
  shapeProps,
  isSelected,
  onSelect,
  onChange,
  setInfo,
}) {
  const shapeRef = useRef();
  const trRef = useRef();

  useEffect(() => {
    if (isSelected) {
      // we need to attach transformer manually
      trRef.current.nodes([shapeRef.current]);
      trRef.current.getLayer().batchDraw();
    }
  }, [isSelected]);

  const handleInfo = () => {
    if (shapeRef && shapeRef.current) {
      const node = shapeRef.current.attrs;
      let { x, y, width, height, scaleX, scaleY, rotation } = node;
      width = width * scaleX;
      height = height * scaleY;
      //   console.log("postman", node);
      setInfo({
        position: {
          x,
          y,
        },
        width,
        height,
        rotate: rotation,
      });
    }
  };

  return (
    <>
      <Rect
        onClick={onSelect}
        onTap={onSelect}
        ref={shapeRef}
        // fillPatternImage={shapeProps.fillPatternImage}
        {...shapeProps}
        draggable
        onDragEnd={(e) => {
          onChange({
            ...shapeProps,
            x: e.target.x(),
            y: e.target.y(),
          });
          handleInfo();
        }}
        onTransformEnd={handleInfo}
      />
      {isSelected && (
        <Transformer
          ref={trRef}
          boundBoxFunc={(oldBox, newBox) => {
            // limit resize
            if (newBox.width < 5 || newBox.height < 5) {
              return oldBox;
            }
            return newBox;
          }}
        />
      )}
    </>
  );
}
