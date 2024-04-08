/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

/// For a given destructurable memory slot, returns whether this operation can
/// rewire its uses of the slot to use the slots generated after
/// destructuring. This may involve creating new operations.
/// 
/// This method must also register the indices it will access within the
/// `usedIndices` set. If the accessor generates new slots mapping to
/// subelements, they must be registered in `mustBeSafelyUsed` to ensure
/// they are used in a safe manner.
/// 
/// No IR mutation is allowed in this method.
bool mlir::DestructurableAccessorOpInterface::canRewire(const ::mlir::DestructurableMemorySlot & slot, ::llvm::SmallPtrSetImpl<::mlir::Attribute> & usedIndices, ::mlir::SmallVectorImpl<::mlir::MemorySlot> & mustBeSafelyUsed, const ::mlir::DataLayout & dataLayout) {
      return getImpl()->canRewire(getImpl(), getOperation(), slot, usedIndices, mustBeSafelyUsed, dataLayout);
  }
/// Rewires the use of a slot to the generated subslots, without deleting
/// any operation. Returns whether the accessor should be deleted.
/// 
/// All IR mutations must happen through the rewriter. Deletion of
/// operations is not allowed, only the accessor can be scheduled for
/// deletion by returning the appropriate value.
::mlir::DeletionKind mlir::DestructurableAccessorOpInterface::rewire(const ::mlir::DestructurableMemorySlot & slot, ::llvm::DenseMap<::mlir::Attribute, ::mlir::MemorySlot> & subslots, ::mlir::RewriterBase & rewriter, const ::mlir::DataLayout & dataLayout) {
      return getImpl()->rewire(getImpl(), getOperation(), slot, subslots, rewriter, dataLayout);
  }
/// Returns the list of slots for which destructuring should be attempted,
/// specifying in which way the slot should be destructured into subslots.
/// The subslots are indexed by attributes. This computes the type of the
/// pointer for each subslot to be generated. The type of the memory slot
/// must implement `DestructurableTypeInterface`.
/// 
/// No IR mutation is allowed in this method.
::llvm::SmallVector<::mlir::DestructurableMemorySlot> mlir::DestructurableAllocationOpInterface::getDestructurableSlots() {
      return getImpl()->getDestructurableSlots(getImpl(), getOperation());
  }
/// Destructures this slot into multiple subslots. The newly generated slots
/// may belong to a different allocator. The original slot must still exist
/// at the end of this call. Only generates subslots for the indices found in
/// `usedIndices` since all other subslots are unused.
/// 
/// The rewriter is located at the beginning of the block where the slot
/// pointer is defined. All IR mutations must happen through the rewriter.
::llvm::DenseMap<::mlir::Attribute, ::mlir::MemorySlot> mlir::DestructurableAllocationOpInterface::destructure(const ::mlir::DestructurableMemorySlot & slot, const ::llvm::SmallPtrSetImpl<::mlir::Attribute> & usedIndices, ::mlir::RewriterBase & rewriter) {
      return getImpl()->destructure(getImpl(), getOperation(), slot, usedIndices, rewriter);
  }
/// Hook triggered once the destructuring of a slot is complete, meaning the
/// original slot is no longer being refered to and could be deleted.
/// This will only be called for slots declared by this operation.
/// 
/// All IR mutations must happen through the rewriter.
void mlir::DestructurableAllocationOpInterface::handleDestructuringComplete(const ::mlir::DestructurableMemorySlot & slot, ::mlir::RewriterBase & rewriter) {
      return getImpl()->handleDestructuringComplete(getImpl(), getOperation(), slot, rewriter);
  }
/// Returns a list of memory slots for which promotion should be attempted.
/// This only considers the local semantics of the allocator, ignoring
/// whether the slot pointer is properly used or not. This allocator is the
/// "owner" of the returned slots, meaning no two allocators should return
/// the same slot. The content of the memory slot must only be reachable
/// using loads and stores to the provided slot pointer, no aliasing is
/// allowed.
/// 
/// Promotion of the slot will lead to the slot pointer no longer being
/// used, leaving the content of the memory slot unreachable.
/// 
/// No IR mutation is allowed in this method.
::llvm::SmallVector<::mlir::MemorySlot> mlir::PromotableAllocationOpInterface::getPromotableSlots() {
      return getImpl()->getPromotableSlots(getImpl(), getOperation());
  }
/// Provides the default Value of this memory slot. The provided Value
/// will be used as the reaching definition of loads done before any store.
/// This Value must outlive the promotion and dominate all the uses of this
/// slot's pointer. The provided rewriter can be used to create the default
/// value on the fly.
/// 
/// The rewriter is located at the beginning of the block where the slot
/// pointer is defined. All IR mutations must happen through the rewriter.
::mlir::Value mlir::PromotableAllocationOpInterface::getDefaultValue(const ::mlir::MemorySlot & slot, ::mlir::RewriterBase & rewriter) {
      return getImpl()->getDefaultValue(getImpl(), getOperation(), slot, rewriter);
  }
/// Hook triggered for every new block argument added to a block.
/// This will only be called for slots declared by this operation.
/// 
/// The rewriter is located at the beginning of the block on call. All IR
/// mutations must happen through the rewriter.
void mlir::PromotableAllocationOpInterface::handleBlockArgument(const ::mlir::MemorySlot & slot, ::mlir::BlockArgument argument, ::mlir::RewriterBase & rewriter) {
      return getImpl()->handleBlockArgument(getImpl(), getOperation(), slot, argument, rewriter);
  }
/// Hook triggered once the promotion of a slot is complete. This can
/// also clean up the created default value if necessary.
/// This will only be called for slots declared by this operation.
/// 
/// All IR mutations must happen through the rewriter.
void mlir::PromotableAllocationOpInterface::handlePromotionComplete(const ::mlir::MemorySlot & slot, ::mlir::Value defaultValue, ::mlir::RewriterBase & rewriter) {
      return getImpl()->handlePromotionComplete(getImpl(), getOperation(), slot, defaultValue, rewriter);
  }
/// Gets whether this operation loads from the specified slot.
/// 
/// No IR mutation is allowed in this method.
bool mlir::PromotableMemOpInterface::loadsFrom(const ::mlir::MemorySlot & slot) {
      return getImpl()->loadsFrom(getImpl(), getOperation(), slot);
  }
/// Gets whether this operation stores to the specified slot.
/// 
/// No IR mutation is allowed in this method.
bool mlir::PromotableMemOpInterface::storesTo(const ::mlir::MemorySlot & slot) {
      return getImpl()->storesTo(getImpl(), getOperation(), slot);
  }
/// Gets the value stored to the provided memory slot, or returns a null
/// value if this operation does not store to this slot. An operation
/// storing a value to a slot must always be able to provide the value it
/// stores. This method is only called once per slot promotion, and only
/// on operations that store to the slot according to the `storesTo` method.
/// The returned value must dominate all operations dominated by the storing
/// operation.
/// 
/// If IR must be mutated to extract a concrete value being stored, mutation
/// must happen through the provided rewriter. The rewriter is located
/// immediately after the memory operation on call. No IR deletion is
/// allowed in this method. IR mutations must not introduce new uses of the
/// memory slot. Existing control flow must not be modified.
::mlir::Value mlir::PromotableMemOpInterface::getStored(const ::mlir::MemorySlot & slot, ::mlir::RewriterBase & rewriter) {
      return getImpl()->getStored(getImpl(), getOperation(), slot, rewriter);
  }
/// Checks that this operation can be promoted to no longer use the provided
/// blocking uses, in the context of promoting `slot`.
/// 
/// If the removal procedure of the use will require that other uses get
/// removed, that dependency should be added to the `newBlockingUses`
/// argument. Dependent uses must only be uses of results of this operation.
/// 
/// No IR mutation is allowed in this method.
bool mlir::PromotableMemOpInterface::canUsesBeRemoved(const ::mlir::MemorySlot & slot, const ::llvm::SmallPtrSetImpl<::mlir::OpOperand *> & blockingUses, ::llvm::SmallVectorImpl<::mlir::OpOperand *> & newBlockingUses, const ::mlir::DataLayout & datalayout) {
      return getImpl()->canUsesBeRemoved(getImpl(), getOperation(), slot, blockingUses, newBlockingUses, datalayout);
  }
/// Transforms IR to ensure that the current operation does not use the
/// provided memory slot anymore. `reachingDefinition` contains the value
/// currently stored in the provided memory slot, immediately before the
/// current operation.
/// 
/// During the transformation, *no operation should be deleted*.
/// The operation can only schedule its own deletion by returning the
/// appropriate `DeletionKind`. The deletion must be legal assuming the
/// blocking uses passed through the `newBlockingUses` list in
/// `canUseBeRemoved` have been removed.
/// 
/// After calling this method, the blocking uses should have disappeared
/// or this operation should have scheduled its own deletion.
/// 
/// This method will only be called after ensuring promotion is allowed via
/// `canUseBeRemoved`. The requested blocking use removal may or may not
/// have been done at the point of calling this method, but it will be done
/// eventually.
/// 
/// The rewriter is located after the promotable operation on call. All IR
/// mutations must happen through the rewriter.
::mlir::DeletionKind mlir::PromotableMemOpInterface::removeBlockingUses(const ::mlir::MemorySlot & slot, const ::llvm::SmallPtrSetImpl<mlir::OpOperand *> & blockingUses, ::mlir::RewriterBase & rewriter, ::mlir::Value reachingDefinition) {
      return getImpl()->removeBlockingUses(getImpl(), getOperation(), slot, blockingUses, rewriter, reachingDefinition);
  }
/// Checks that this operation can be promoted to no longer use the provided
/// blocking uses, in order to allow optimization.
/// 
/// If the removal procedure of the use will require that other uses get
/// removed, that dependency should be added to the `newBlockingUses`
/// argument. Dependent uses must only be uses of results of this operation.
/// 
/// No IR mutation is allowed in this method.
bool mlir::PromotableOpInterface::canUsesBeRemoved(const ::llvm::SmallPtrSetImpl<::mlir::OpOperand *> & blockingUses, ::llvm::SmallVectorImpl<::mlir::OpOperand *> & newBlockingUses, const ::mlir::DataLayout & datalayout) {
      return getImpl()->canUsesBeRemoved(getImpl(), getOperation(), blockingUses, newBlockingUses, datalayout);
  }
/// Transforms IR to ensure that the current operation does not use the
/// provided blocking uses anymore. In contrast to
/// `PromotableMemOpInterface`, operations implementing this interface
/// must not need access to the reaching definition of the content of the
/// slot.
/// 
/// During the transformation, *no operation should be deleted*.
/// The operation can only schedule its own deletion by returning the
/// appropriate `DeletionKind`. The deletion must be legal assuming the
/// blocking uses passed through the `newBlockingUses` list in
/// `canUseBeRemoved` have been removed.
/// 
/// After calling this method, the blocking uses should have disappeared
/// or this operation should have scheduled its own deletion.
/// 
/// This method will only be called after ensuring promotion is allowed via
/// `canUseBeRemoved`. The requested blocking use removal may or may not
/// have been done at the point of calling this method, but it will be done
/// eventually.
/// 
/// The rewriter is located after the promotable operation on call. All IR
/// mutations must happen through the rewriter.
::mlir::DeletionKind mlir::PromotableOpInterface::removeBlockingUses(const ::llvm::SmallPtrSetImpl<mlir::OpOperand *> & blockingUses, ::mlir::RewriterBase & rewriter) {
      return getImpl()->removeBlockingUses(getImpl(), getOperation(), blockingUses, rewriter);
  }
/// This method allows the promoted operation to visit the SSA values used
/// in place of the memory slot once the promotion process of the memory
/// slot is complete.
/// 
/// If this method returns true, the `visitReplacedValues` method on this
/// operation will be called after the main mutation stage finishes
/// (i.e., after all ops have been processed with `removeBlockingUses`).
/// 
/// Operations should only the replaced values if the intended
/// transformation applies to all the replaced values. Furthermore, replaced
/// values must not be deleted.
bool mlir::PromotableOpInterface::requiresReplacedValues() {
      return getImpl()->requiresReplacedValues(getImpl(), getOperation());
  }
/// Transforms the IR using the SSA values that replaced the memory slot.
/// 
/// This method will only be called after all blocking uses have been
/// scheduled for removal and if `requiresReplacedValues` returned
/// true.
/// 
/// The rewriter is located after the promotable operation on call. All IR
/// mutations must happen through the rewriter. During the transformation,
/// *no operation should be deleted*.
void mlir::PromotableOpInterface::visitReplacedValues(::llvm::ArrayRef<std::pair<::mlir::Operation*, ::mlir::Value>> mutatedDefs, ::mlir::RewriterBase & rewriter) {
      return getImpl()->visitReplacedValues(getImpl(), getOperation(), mutatedDefs, rewriter);
  }
/// Returns whether all accesses in this operation to the provided slot are
/// done in a safe manner. To be safe, the access most only access the slot
/// inside the bounds that its type implies.
/// 
/// If the safety of the accesses depends on the safety of the accesses to
/// further memory slots, the result of this method will be conditioned to
/// the safety of the accesses to the slots added by this method to
/// `mustBeSafelyUsed`.
/// 
/// No IR mutation is allowed in this method.
::mlir::LogicalResult mlir::SafeMemorySlotAccessOpInterface::ensureOnlySafeAccesses(const ::mlir::MemorySlot & slot, ::mlir::SmallVectorImpl<::mlir::MemorySlot> & mustBeSafelyUsed, const ::mlir::DataLayout & dataLayout) {
      return getImpl()->ensureOnlySafeAccesses(getImpl(), getOperation(), slot, mustBeSafelyUsed, dataLayout);
  }
