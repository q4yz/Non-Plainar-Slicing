import trimesh
import numpy as np

from .utils import checkForVerticesOnPlain
from .transformation import rotate_to_align
import globals

def multisplit(mesh: trimesh.Trimesh, normal, steps : np.array):
    """
    Rotates the mesh so the normal aligns with (0, 0, z),
    translates it to the starting position, and applies `splitFacesOnZZero` 
    at each step along the z-axis.
    """
    # Rotate the mesh to align the normal with (0, 0, 1)

    rotation_matrix : np.array =  rotate_to_align(normal, target=(0, 0, 1))
    mesh.apply_transform(rotation_matrix)

    applyedOffset : float = 0
    
    i= 0
    totalSteps = len(steps)
    for step in steps:
        # Translate the mesh by the step in the z direction

        globals.progress2 = i / float(totalSteps)

        step_translation = trimesh.transformations.translation_matrix([0, 0, -step -applyedOffset])
        applyedOffset = -step
        mesh.apply_transform(step_translation)

        # Split the faces on the z=0 plane
        mesh = splitFacesOnZZero(mesh)

        i+= 1


    translation_vector = [0, 0, -applyedOffset]
    translation_matrix = trimesh.transformations.translation_matrix(translation_vector)
    mesh.apply_transform(translation_matrix)

    inverse_rotation_matrix = np.linalg.inv(rotation_matrix)
    mesh.apply_transform(inverse_rotation_matrix)

    globals.progress2 = 0

    return mesh


def splitFacesOnZZero(mesh:trimesh.Trimesh) -> trimesh.Trimesh: 

    old_v : np.array = mesh.vertices
    old_f : np.array = mesh.faces
    old_v = np.array(old_v)

    if checkForVerticesOnPlain(old_v):
        print("warning points on Plain")
   
    maskVerticesAbovePlain = old_v[:, 2] > 0

    maskFacesAbove = np.all(maskVerticesAbovePlain[old_f], axis=1)

    maskVerticesBelowPlain = old_v[:, 2] < 0

    maskFacesBelow = np.all(maskVerticesBelowPlain[old_f], axis=1)
    
    MaskNonIntersectingFaces = np.logical_or(maskFacesAbove, maskFacesBelow)

    unchangedFaces = old_f[MaskNonIntersectingFaces]

    intersectingFaces = old_f[~MaskNonIntersectingFaces]

    # Invert rows with exactly two `True` values
    maskSingleValue = np.full((len(intersectingFaces), 3), False)
    for i,f in enumerate(intersectingFaces):
        if np.sum(maskVerticesAbovePlain[f]) == 1:
            maskSingleValue[i] = [maskVerticesAbovePlain[v] for v in f]
        else:
            maskSingleValue[i] = [~maskVerticesAbovePlain[v] for v in f]

        # Rotate each row to move the first True to the beginning

    for i in range(maskSingleValue.shape[0]):
        # Find the index of the first True value in the row
        true_index = np.argmax(maskSingleValue[i])
    
        # If a True is found, rotate the row so that the True value comes to the front
        if true_index != 0:  # Only rotate if the first True is not already at the front
            maskSingleValue[i] = np.roll(maskSingleValue[i], -true_index)
            intersectingFaces[i] = np.roll(intersectingFaces[i], -true_index)

    newFaces = np.full((len(intersectingFaces) * 3, 3), 0)
    
    newVerices = np.full((len(intersectingFaces) * 2, 3), 0)
    newVerices = np.vstack([old_v, newVerices])

    def findIntersectionOnZPlain(v1, v2):
        # Calculate t for the intersection on the z = 0 plane
        t = -v1[2] / (v2[2] - v1[2])
        # Calculate the intersection point v12
        v12 = v1 + t * (v2 - v1)
        return v12

    for i,f in enumerate(intersectingFaces):
        indexV1 = f[0]
        indexV2 = f[1]
        indexV3 = f[2]
        v1 = old_v[indexV1]
        v2 = old_v[indexV2]
        v3 = old_v[indexV3]
        indexV12 = i*2 + len(old_v)
        indexV13 = i*2 + 1 + len(old_v)
        v12 = findIntersectionOnZPlain(v1, v2)
        v13 = findIntersectionOnZPlain(v1, v3)

        newVerices[indexV12] = v12
        newVerices[indexV13] = v13

        newFaces[i * 3] = (indexV1,indexV12,indexV13)
        newFaces[i * 3 + 1] = (indexV13,indexV12,indexV2)
        newFaces[i * 3 + 2] = (indexV2,indexV3,indexV13)

    newFaces = np.vstack([unchangedFaces, newFaces])
    mesh = trimesh.Trimesh(vertices=newVerices, faces=newFaces)

    return mesh







