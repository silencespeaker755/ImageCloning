import numpy as np
import cv2
import pygalmesh
from multiprocessing import Pool

from time import perf_counter

class timer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.time = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.time = perf_counter() - self.time
        print(f"{self.name } took {self.time:.3f} seconds")

class MVCCloner:
    def __init__(self):
        pass

    # @staticmethod
    # def unitVector(vec):
    #     return vec / np.linalg.norm(vec)

    # @staticmethod
    # def angleBetween(pA, pO, pB):
    #     ''' Calculate ∢ pA, pO, pB
    #     '''
    #     vOA = MVCCloner.unitVector(pA - pO)
    #     vOB = MVCCloner.unitVector(pB - pO)
    #     return np.arccos(np.clip(np.dot(vOA, vOB), -1.0, 1.0))

    @staticmethod
    def unitVectors(vecs):
        return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

    @staticmethod
    def anglesBetween(pAs, pO, pBs):
        ''' Calculate ∢ pAs, pO, pBs
        '''
        vOAs = MVCCloner.unitVectors(pAs - pO)
        vOBs = MVCCloner.unitVectors(pBs - pO)
        return np.arccos(np.clip(np.einsum('ij,ij->i', vOAs, vOBs), -1.0, 1.0))

    def calcBoundaryContour(self):
        canvas = np.zeros(self.src.shape[:2], dtype=np.uint8)
        canvas = cv2.fillPoly(canvas, [np.flip(self.boundaryPolygon, axis=1)], 1)
        canvas = cv2.erode(canvas, np.ones((5, 5), np.uint8), iterations=1)
        contours, _ = cv2.findContours(canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.boundary = np.flip(contours[0].squeeze(1), axis=1)

    def buildBoundaryHierarchy(self, coarsestLevelMaximumNumberOfPoint=16):
        self.hierarchy = [np.array(range(len(self.boundary)))]
        while len(self.hierarchy[-1]) > coarsestLevelMaximumNumberOfPoint:
            self.hierarchy.append(self.hierarchy[-1][::2])
        self.hierarchy = self.hierarchy[::-1]

    def sampleBoundary(self, queryPoint):
        εDistFunc = lambda level: len(self.boundary) / (16 * 2.5 ** level)
        εAngFunc = lambda level: 0.75 * 0.8 ** level

        samples = [list(range(len(self.hierarchy[0])))]
        while True:
            curLevel = len(samples) - 1
            εDist = εDistFunc(curLevel)
            εAng = εAngFunc(curLevel)
            
            if curLevel == len(self.hierarchy) - 1:
                break

            nextLevelSamples = set()

            xs = self.boundary[self.hierarchy[curLevel][samples[-1]]]
            xpres = self.boundary[np.roll(self.hierarchy[curLevel], 1)[samples[-1]]]
            xnxts = self.boundary[np.roll(self.hierarchy[curLevel], -1)[samples[-1]]]
            dists = np.linalg.norm(xs - queryPoint, axis=1)
            anglePres = self.anglesBetween(xpres, queryPoint, xs)
            angleNxts = self.anglesBetween(xs, queryPoint, xnxts)

            for idx, sample in enumerate(samples[-1]):
                if dists[idx] > εDist and anglePres[idx] < εAng and angleNxts[idx] < εAng:
                    continue

                nextLevelSamples.add((sample*2-1) % len(self.hierarchy[curLevel+1]))
                nextLevelSamples.add(sample*2)
                nextLevelSamples.add((sample*2+1) % len(self.hierarchy[curLevel+1]))

            if not nextLevelSamples:
                break

            samples.append(list(nextLevelSamples))

        # convert to boundary index
        samples = [[self.hierarchy[level][sample] for sample in levelSamples] for level, levelSamples in enumerate(samples)]

        # make them disjoint
        for i in range(len(samples)-1, 0, -1):
            samples[i] = np.array(sorted(set(samples[i]) - set(samples[i-1])))

        return samples

    def calcAdaptiveMesh(self, max_circumradius_shortest_edge_ratio=1.41421356237, max_edge_size=0.0, num_lloyd_steps=0):
        # The default arguments are copied from pygalmesh's definition
        # These arguments need to be adjusted carefully
        constraints = [[i, (i+1) % len(self.boundary)] for i in range(len(self.boundary))]
        mesh = pygalmesh.generate_2d(
                self.boundary,
                constraints,
                max_circumradius_shortest_edge_ratio,
                max_edge_size,
                num_lloyd_steps,
        )
        self.meshPoints = mesh.points
        self.meshTriangles = mesh.cells_dict['triangle']

    def calcBarycentricCoordinates(self):
        # for every pixel, find the corresponding triangle
        self.triangleIndices = np.full(self.src.shape[:2], -1, dtype=np.int32)
        triangleVertices = self.meshPoints[self.meshTriangles]
        for triangleIndex, triangle in enumerate(triangleVertices):
            cv2.fillConvexPoly(self.triangleIndices, np.rint(np.flip(triangle, axis=1)).astype(np.int32), triangleIndex)

        # calculate barycentric coordinate
        # may contain garbage value (when triangleIndices == -1)

        Y1 = triangleVertices[:, 0, 0]
        Y2 = triangleVertices[:, 1, 0]
        Y3 = triangleVertices[:, 2, 0]
        X1 = triangleVertices[:, 0, 1]
        X2 = triangleVertices[:, 1, 1]
        X3 = triangleVertices[:, 2, 1]
        detT = (Y2 - Y3) * (X1 - X3) + (X3 - X2) * (Y1 - Y3)
        Y, X = np.mgrid[0:self.src.shape[0], 0:self.src.shape[1]]
        λ1 = ((Y2[self.triangleIndices] - Y3[self.triangleIndices]) *
              (X - X3[self.triangleIndices]) +
              (X3[self.triangleIndices] - X2[self.triangleIndices]) *
              (Y - Y3[self.triangleIndices])) / detT[self.triangleIndices]
        λ2 = ((Y3[self.triangleIndices] - Y1[self.triangleIndices]) *
              (X - X3[self.triangleIndices]) +
              (X1[self.triangleIndices] - X3[self.triangleIndices]) *
              (Y - Y3[self.triangleIndices])) / detT[self.triangleIndices]
        λ3 = 1 - λ1 - λ2

        #X = triangleVertices[:, :, 0][self.triangleIndices]
        #Y = triangleVertices[:, :, 1][self.triangleIndices]
        #A = np.stack([np.ones(X), X, Y], axis=2)
        #b = np.stack([], axis=)
        #self.barycentric = np.linalg.solve(A, b)

        self.barycentric = np.dstack([λ1, λ2, λ3])
        self.barycentric = np.clip(self.barycentric, 0.0, 1.0)
        self.barycentric = self.barycentric / self.barycentric.sum(axis=2, keepdims=True)
    
    def calcMVC(self):
        with timer('sample'):
            with Pool(4) as p:
                self.meshPointBoundarySamples = p.map(self.sampleBoundary, self.meshPoints)
        self.meshPointFlattenBoundarySamples = [np.sort([y for x in samples for y in x]) for samples in self.meshPointBoundarySamples]
        self.meshPointMVC = []
        for meshPoint, boundarySamples in zip(self.meshPoints, self.meshPointFlattenBoundarySamples):
            lenXP = np.linalg.norm(self.boundary[boundarySamples] - meshPoint, axis=1)

            '''
            angles = []
            for idx in range(len(boundarySamples)):
                nxtIdx = (idx + 1) % len(boundarySamples)
                boundaryPoint = self.boundary[boundarySamples[idx]]
                boundaryPointNxt = self.boundary[boundarySamples[nxtIdx]]
                angles.append(angleBetween(boundaryPoint, meshPoint, boundaryPointNxt))
            angles = np.array(angles)
            '''
            angles = self.anglesBetween(self.boundary[boundarySamples], meshPoint, self.boundary[np.roll(boundarySamples, -1)])
            tanHalfAngles = np.tan(angles / 2)
            w = (tanHalfAngles + np.roll(tanHalfAngles, 1)) / lenXP

            # workaround. may not work properly
            w[np.isnan(w)] = 1e9

            λ = w / w.sum()
            self.meshPointMVC.append(λ)

    def calcMeanValueInterpolants(self, diff):
        ''' this is not doc. this is commented-out code block
        ## hierarchical version (different level -> different blur level)
        ## hard to implement now. To implement: make MVC hierarchical

        diffPyramid = [cv2.GaussianBlur(diff, (5, 5), 0)]
        for i in range(len(self.hierarchy) - 1):
            diffPyramid.append(cv2.GaussianBlur(diffPyramid[-1], (3, 3), 0))

        R = []
        for pointId, boundarySamples in enumerate(self.meshPointBoundarySamples):
            r = 0
            for level, levelSamples in enumerate(boundarySamples):
                ...
        '''
        diff = cv2.GaussianBlur(diff, (5, 5), 0)
        R = []
        for λ, boundarySamples in zip(self.meshPointMVC, self.meshPointFlattenBoundarySamples):
            sampledPoints = self.boundary[boundarySamples]
            r = np.dot(λ, diff[sampledPoints[:, 0], sampledPoints[:, 1]])
            R.append(r)

        return np.array(R)

    def barycentricInterpolate(self, meanValueInterpolants):
        rImg = np.einsum('ijk,ijkl->ijl', self.barycentric, meanValueInterpolants[self.meshTriangles[self.triangleIndices]])
        rImg[self.triangleIndices == -1] = 0
        #cv2.imshow('123123', rImg)
        #cv2.waitKey()
        return rImg

    def preprocessSourceImage(self, src, boundaryPolygon):
        self.src = src
        self.boundaryPolygon = boundaryPolygon

        self.calcBoundaryContour()
        self.buildBoundaryHierarchy()
        self.calcAdaptiveMesh(max_edge_size=20, num_lloyd_steps=0)
        self.calcBarycentricCoordinates()
        with timer('MVC'):
            self.calcMVC()

    def computeCloning(self, dest, location):
        #diff = dest[self.boundary[:, 0], self.boundary[:, 1]] - self.src[self.boundary[:, 0], self.boundary[:, 1]]
        # location -> image center
        anchor = location - np.array(self.src.shape[:2]) // 2
        anchor = np.clip(anchor, 0, None)
        destPatch = dest[anchor[0]:anchor[0]+self.src.shape[0], anchor[1]:anchor[1]+self.src.shape[1]]
        diff = destPatch - self.src
        meanValueInterpolants = self.calcMeanValueInterpolants(diff)
        rImg = self.barycentricInterpolate(meanValueInterpolants)

        mask = (self.triangleIndices != -1).astype(np.uint8)
        cloneResult = np.where(np.repeat((mask)[:, :, np.newaxis], 3, axis=2), self.src + rImg, destPatch)

        finalImage = dest
        finalImage[anchor[0]:anchor[0]+self.src.shape[0], anchor[1]:anchor[1]+self.src.shape[1]] = cloneResult
        return finalImage

    def clone(self, src, dest, boundaryPolygon, location):
        ''' You only need to call this function
        '''
        src = src.astype(np.float32) / 255
        dest = dest.astype(np.float32) / 255
        self.preprocessSourceImage(src, boundaryPolygon)
        return self.computeCloning(dest, location)


if __name__ == '__main__':
    cloner = MVCCloner()
    img = cv2.imread('static/images/src1.png')
    dest = cv2.imread('static/images/dst1.png')
    poly = np.array([[50, 10], [50, 390], [210, 390], [210, 10]])
    ret = cloner.clone(img, dest, poly, np.array([200, 1000]))
    cv2.imshow('result', ret)
    cv2.waitKey()

    ## check boundary
    print("boundary length:", len(cloner.boundary))
    canvas = np.zeros(img.shape, dtype=np.uint8)
    for x in cloner.boundary:
        canvas = cv2.circle(canvas, x[::-1], radius=0, color=(255, 255, 255), thickness=-1)
    cv2.imshow('1', canvas)
    cv2.waitKey()

    ## check hierarchy
    print(cloner.hierarchy[:3])
    for i in range(3):
        canvas = np.zeros(img.shape, dtype=np.uint8)
        for x in cloner.boundary:
            canvas = cv2.circle(canvas, x[::-1], radius=0, color=(255, 255, 255), thickness=-1)
        for x in cloner.boundary[cloner.hierarchy[i]]:
            canvas = cv2.circle(canvas, x[::-1], radius=3, color=(255, 0, 0), thickness=-1)
        cv2.imshow(f'hierarchy{i}', canvas)
        cv2.waitKey()
    
    ## check mesh
    print("mesh length:", len(cloner.meshPoints))
    canvas = np.zeros(img.shape, dtype=np.uint8)
    for x in cloner.meshTriangles:
        x1, x2, x3 = np.rint(cloner.meshPoints[x]).astype(np.int32)
        x1 = x1[::-1]
        x2 = x2[::-1]
        x3 = x3[::-1]
        canvas = cv2.line(canvas, x1, x2, color=(255, 0, 0), thickness=1)
        canvas = cv2.line(canvas, x2, x3, color=(255, 0, 0), thickness=1)
        canvas = cv2.line(canvas, x1, x3, color=(255, 0, 0), thickness=1)
    for x in cloner.meshPoints:
        canvas = cv2.circle(canvas, np.rint(x[::-1]).astype(np.int32), radius=3, color=(0, 0, 255), thickness=-1)
    cv2.imshow('2', canvas)
    cv2.waitKey()

    ## check triangle indices
    canvas = cloner.triangleIndices / len(cloner.meshTriangles)
    cv2.imshow('3', canvas)
    cv2.waitKey()

    ## check barycentric
    print("some barycentric coords")
    cv2.imshow('bary', cloner.barycentric)
    cv2.waitKey()

    ## need to take the points inside the polygon
    print(cloner.barycentric[50:55, 50:55])
    print(cloner.barycentric[100:105, 100:105])

    ## check sample
    for idx in [-1, -10, -100, 0, 10, 100]:
        canvas = np.zeros(img.shape, dtype=np.uint8)
        for x in cloner.boundary:
            canvas = cv2.circle(canvas, x[::-1], radius=0, color=(255, 255, 255), thickness=-1)
        p = cloner.meshPoints[idx]
        s = cloner.boundary[cloner.meshPointFlattenBoundarySamples[idx]]
        print(cloner.meshPointFlattenBoundarySamples[idx])
        for x in s:
            canvas = cv2.circle(canvas, np.rint(x[::-1]).astype(np.int32), radius=3, color=(0, 0, 255), thickness=-1)
        canvas = cv2.circle(canvas, np.rint(p[::-1]).astype(np.int32), radius=5, color=(255, 0, 0), thickness=-1)
        cv2.imshow(f'sample{idx}', canvas)
        cv2.waitKey()
